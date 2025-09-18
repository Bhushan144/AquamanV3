# backend/api.py (Cleaned Version)

import pandas as pd
import re
import ast
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Tuple
from collections import defaultdict, deque

# Import the agent_executor AND the db object from agent.py
from backend.agent import agent_executor, db, model

# --- Database Connection for Pandas ---
# We get the engine directly from the imported db object.
engine = db._engine

# --- Pydantic Models for API Data Validation ---
class ChatRequest(BaseModel):
    input: str
    session_id: Optional[str] = None
    force_sql: Optional[bool] = False

class ChatResponse(BaseModel):
    output: str
    table_data: Optional[List[Dict[str, Any]]] = None
    geo_data: Optional[List[Dict[str, Any]]] = None
    sql_query: Optional[str] = None

# --- FastAPI Application Setup ---
app = FastAPI(
    title="Aquaman AI Backend",
    description="API server for the ARGO float data conversational agent."
)

# --- Simple in-process session memory (last 5 turns) ---
_session_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=5))
_session_state: Dict[str, Dict[str, Any]] = defaultdict(dict)


def _extract_top_n_from_text(text: str) -> Optional[int]:
    try:
        m = re.search(r"top\s+(\d+)", text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None


def _rule_based_sql(prompt: str, schema: str, session_state: Dict[str, Any]) -> Tuple[str, str]:
    """
    Return (sql, reason) using simple heuristics for common intents.
    """
    p = prompt.lower()
    # Top N profiles by average temperature
    if ("average" in p and "temperature" in p) or ("avg" in p and "temp" in p):
        n = _extract_top_n_from_text(prompt) or 5
        sql = (
            "SELECT m.profile_id, ROUND(AVG(m.temperature_celsius)::numeric, 2) AS avg_temperature_celsius "
            "FROM measurements m "
            "GROUP BY m.profile_id "
            "ORDER BY avg_temperature_celsius DESC "
            f"LIMIT {n};"
        )
        return sql, f"heuristic: top {n} profiles by average temperature"

    # Follow-up: where are they located
    if ("where are" in p or "location" in p or "located" in p) and session_state.get("last_profile_ids"):
        ids = session_state["last_profile_ids"]
        id_list = ",".join(str(int(x)) for x in ids)
        sql = (
            "SELECT DISTINCT ON (p.profile_id) p.profile_id, p.latitude, p.longitude, p.timestamp "
            "FROM profiles p "
            f"WHERE p.profile_id IN ({id_list}) "
            "ORDER BY p.profile_id, p.timestamp DESC;"
        )
        return sql, "heuristic: latest location for prior selection"

    return "", ""

# --- CORS Configuration ---
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- API Endpoints ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    table_data = None
    geo_data = None
    sql_query_found = ""

    # Build lightweight conversational context from stored history
    sid = request.session_id or "default"
    turns = list(_session_history[sid])
    context_lines = []
    for role, content in turns:
        prefix = "User:" if role == "user" else "Assistant:"
        context_lines.append(f"{prefix} {content}")
    context_block = "\n".join(context_lines)
    composed_input = (
        f"{('Conversation so far:\n' + context_block + '\n') if context_block else ''}"
        f"User: {request.input}\n"
        f"Please answer concisely and produce SQL if needed."
    )

    # Run the agent to get the response (with graceful fallback on parsing errors)
    response = {}
    agent_output = ""
    try:
        if not request.force_sql:
            response = await agent_executor.ainvoke(
                {"input": composed_input},
                config={"return_intermediate_steps": True}
            )
            agent_output = response.get("output", "") or ""
        else:
            response = {}
            agent_output = ""
    except Exception as e:
        # Allow pipeline to continue to SQL fallback without surfacing raw errors to users
        print(f"Agent error (continuing with SQL fallback): {e}")
        agent_output = ""

    # --- Robust SQL extraction from multiple possible places ---
    candidate_sqls = []

    # 1) Look for an explicit SQL in the text (not tied to "Action Input:")
    def extract_selects(text: str):
        if not text:
            return []
        # Find first SELECT ... up to semicolon or end
        selects = re.findall(r"(?is)\bSELECT\b[\s\S]*?(?:;|$)", text or "")
        cleaned = []
        for s in selects:
            s2 = s
            # Trim common agent tokens trailing after the SQL
            for token in ["Observation:", "Thought:", "Final Answer:"]:
                if token in s2:
                    s2 = s2.split(token)[0]
            cleaned.append(s2.strip())
        return [c for c in cleaned if c.upper().startswith("SELECT")] 

    candidate_sqls.extend(extract_selects(agent_output))

    # 2) Check intermediate steps if available
    inter = response.get("intermediate_steps")
    if inter:
        try:
            for step in inter:
                # step could be (AgentAction, Any) or dict-like; cast to string and scan
                candidate_sqls.extend(extract_selects(str(step)))
        except Exception:
            pass

    # 3) Deduplicate while preserving order
    seen = set()
    unique_sqls = []
    for s in candidate_sqls:
        key = s.strip()
        if key and key not in seen:
            seen.add(key)
            unique_sqls.append(key)

    # Choose the first plausible SQL
    if unique_sqls:
        sql_query_found = unique_sqls[0]

    # Fallback 1: rule-based SQL for common intents
    if not sql_query_found:
        schema = db.get_table_info()
        sql_rb, reason = _rule_based_sql(request.input, schema, _session_state[sid])
        if sql_rb:
            sql_query_found = sql_rb

    # Fallback 2: ask the LLM to generate a SELECT given the schema if still none was found
    if not sql_query_found:
        try:
            schema = db.get_table_info()
            fallback_prompt = (
                "You are a SQL assistant for a PostgreSQL database.\n"
                "Given the database schema and the user's question, write a single valid SQL SELECT query.\n"
                "Constraints:\n"
                "- Output ONLY the SQL SELECT, no commentary.\n"
                "- Use correct table and column names from the schema.\n\n"
                f"Schema:\n{schema}\n\n"
                f"Question: {request.input}\n\n"
                "SQL:"
            )
            llm_msg = await model.ainvoke(fallback_prompt)
            llm_text = getattr(llm_msg, "content", str(llm_msg))
            extracted = extract_selects(llm_text)
            if extracted:
                sql_query_found = extracted[0]
        except Exception as e:
            print(f"Fallback SQL generation failed: {e}")

    # Execute SQL if found
    if sql_query_found.upper().startswith("SELECT"):
        try:
            df = pd.read_sql_query(sql_query_found, engine)
            table_data = df.to_dict(orient="records")
            if "latitude" in df.columns and "longitude" in df.columns:
                geo_data = table_data
            if not agent_output:
                # Create a concise summary from common result shapes
                try:
                    if {"profile_id", "avg_temperature_celsius"}.issubset(df.columns):
                        topn = min(3, len(df))
                        samples = ", ".join(
                            f"profile_id {int(df.iloc[i]['profile_id'])} ({float(df.iloc[i]['avg_temperature_celsius']):.2f}°C)"
                            for i in range(topn)
                        )
                        agent_output = f"Top results by average temperature: {samples}."
                    elif {"profile_id", "latitude", "longitude"}.issubset(df.columns):
                        topn = min(3, len(df))
                        samples = ", ".join(
                            f"{int(df.iloc[i]['profile_id'])}: ({float(df.iloc[i]['latitude']):.3f}, {float(df.iloc[i]['longitude']):.3f})"
                            for i in range(topn)
                        )
                        agent_output = f"Locations for selected profiles: {samples}."
                    else:
                        agent_output = "Showing results generated from SQL."
                except Exception:
                    agent_output = "Showing results generated from SQL."

            # Save selected profile_ids for follow-ups
            if "profile_id" in df.columns:
                _session_state[sid]["last_profile_ids"] = [r["profile_id"] for r in table_data if r.get("profile_id") is not None]
        except Exception as e:
            print(f"Error running captured SQL query with Pandas: {e}")

    # Store the turn for session memory
    _session_history[sid].append(("user", request.input))
    _session_history[sid].append(("assistant", agent_output))

    return ChatResponse(
        output=agent_output,
        table_data=table_data,
        geo_data=geo_data,
        sql_query=sql_query_found,
    )

@app.get("/")
def root():
    return {"status": "ok", "message": "Welcome to the Aquaman AI Backend"}