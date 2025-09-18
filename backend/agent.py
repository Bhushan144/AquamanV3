# backend/agent.py (Corrected Version)

import os
from dotenv import load_dotenv

# --- IMPORTS ---
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

# --- Load Environment Variables ---
load_dotenv()

# --- INITIALIZATION of LLM and DB ---
try:
    # Setup Database connection (remains the same)
    db = SQLDatabase.from_uri(os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/Aquaman"))

    # Setup the Hugging Face Language Model using your chosen model
    llm_endpoint = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen3-Next-80B-A3B-Instruct",
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        task="text-generation"
    )
    model = ChatHuggingFace(llm=llm_endpoint)

    # Setup the SQL Toolkit and tools (filter out checker)
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    tools = toolkit.get_tools()
    tools_without_checker = [tool for tool in tools if "checker" not in tool.name]

    # --- Conversation memory (last 5 exchanges) ---
    memory = ConversationBufferWindowMemory(
        k=5,
        memory_key="chat_history",
        return_messages=True,
    )

    # --- ReAct-style agent with user's prompt structure ---
    prompt = PromptTemplate(
        template=(
            "you are an agentic chatbot which will give the answers in natutal language using the database tool you have "
            "or you can also answer the general queries too directly without any tools , so Answer the following questions as best you can and remember you should not use the sql query which will return the output that will extend the context window example : select * from table etc instead use aggregrate operations and there and only two tables in database profiles and measurements . You have access to the following tools:\n\n{tools}\n\n"
            "Use the following format:\n\n"
            "Question: the input question you must answer\n"
            "Thought: you should always think about what to do\n"
            "Action: the action to take, should be one of [{tool_names}]\n"
            "Action Input: the input to the action\n"
            "Observation: the result of the action\n"
            "... (this Thought/Action/Action Input/Observation can repeat N times)\n"
            "Thought: I now know the final answer\n\n"
            " Final Answer: the final answer to the original input question\n\n"
            "Begin! \n\n Previous conversation history: \n\n {chat_history} \n\nNew question: {input} \n\n Thought:{agent_scratchpad}"
        ),
        input_variables=["agent_scratchpad", "input", "tool_names", "tools", "chat_history"],
    )

    agent = create_react_agent(
        llm=model,
        tools=tools_without_checker,
        prompt=prompt,
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools_without_checker,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
    )

except Exception as e:
    print(f"FATAL ERROR: Could not initialize the agent service: {e}")
    agent_executor = None