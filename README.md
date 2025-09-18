# Aquaman

Run the project locally

1. Create and activate virtual environment
   - Windows PowerShell
     - `python -m venv venv`
     - `./venv/Scripts/Activate.ps1`
2. Install dependencies
   - `pip install -r requirements.txt`
3. Create `.env` in project root with:
   - `HUGGINGFACEHUB_API_TOKEN=your_hf_token`
   - `DATABASE_URL=postgresql://postgres:123456@localhost:5432/Aquaman`
4. Ensure database exists and tables are created (SQL below). Optionally ingest sample NetCDF via `python backend/test.py` after updating `DB_URL`/file path if needed.

Note: 

agent.py --> contains the ai agent to run sql queries.

test.py --> has the code to store .nc data into structured format
  <ul> to create the database you can use : </ul>
  CREATE TABLE profiles (
    profile_id SERIAL PRIMARY KEY, 
    float_wmo_id BIGINT,
    timestamp TIMESTAMPTZ, 
    latitude REAL,
    longitude REAL,
    UNIQUE (float_wmo_id, timestamp)
  );

  CREATE TABLE measurements (
      measurement_id SERIAL PRIMARY KEY, 
      profile_id BIGINT,
      pressure_dbar REAL,
      temperature_celsius REAL,
      salinity_psu REAL,
      FOREIGN KEY (profile_id) REFERENCES profiles(profile_id)
  );

brain.py --> just a file i was experimenting (not yet imp )

----------------------------------------------------------------------------------------

Activate virtual environment:
`./venv/Scripts/Activate.ps1`

To run the frontend:
`streamlit run frontend/app.py --server.port 8501`

To run the backend 
`uvicorn backend.api:app --reload --port 8000`

Connectivity checklist
- Backend must be running on `http://127.0.0.1:8000`
- Frontend uses API URL `http://127.0.0.1:8000/chat` in `frontend/app.py`
- CORS allows `http://localhost:8501` by default in `backend/api.py`
- Test backend: `Invoke-WebRequest -Uri http://127.0.0.1:8000/ | Select-Object -ExpandProperty Content`
- Test chat endpoint: `Invoke-WebRequest -Uri http://127.0.0.1:8000/chat -Method POST -Body '{"input":"hello"}' -ContentType 'application/json' | Select-Object -ExpandProperty Content`

Tables DDL (PostgreSQL)
```
CREATE TABLE profiles (
    profile_id SERIAL PRIMARY KEY,
    float_wmo_id BIGINT,
    profile_date DATE,    -- Changed
    profile_time TIME,    -- Added
    latitude REAL,
    longitude REAL,
    UNIQUE (float_wmo_id, profile_date, profile_time) -- Changed
);

CREATE TABLE measurements (
    measurement_id SERIAL PRIMARY KEY,
    profile_id BIGINT REFERENCES profiles(profile_id),
    pressure_dbar REAL,
    temperature_celsius REAL,
    salinity_psu REAL,
    doxy_umol_kg REAL,       -- BGC: Dissolved Oxygen
    chla_mg_m3 REAL,         -- BGC: Chlorophyll-a
    nitrate_umol_kg REAL     -- BGC: Nitrate
);
```

Notes on visualizations
- Chat response is shown on the right.
- Left panel renders:
  - SQL used (if detected),
  - Map when `latitude` and `longitude` exist,
  - Table for any tabular data,
  - Time series when a time column and numeric columns exist,
  - Vertical profiles when `pressure_dbar` with `temperature_celsius`/`salinity_psu` are present,
  - CSV download of the table.