# Capitol Trades Tracker

Capitol Trades Tracker is a FastAPI + SQLite demo app that surfaces US politician stock trade disclosures with computed performance metrics versus SPY. Disclosures are public and can be delayed; this project is for informational purposes only and is **not investment advice**.

## Features
- Polished, server-rendered UI with leaderboards, filtering, and responsive tables.
- Politician profile pages with trade history and performance snapshots.
- Ingestion pipeline supporting multiple sources (sample JSON included).
- Transparent performance metrics (excess return vs SPY over 1y/5y windows).

## Prerequisites
- Python 3.11+

## Setup (macOS/Linux)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run ingestion (sample data)
```bash
python scripts/run_ingestion.py
```

## Run the server (local dev)
```bash
python -m uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000` to view the app.

## Production-style command
```bash
PORT=8000 python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
```

## Tests
```bash
pytest
```

## Project structure
```
app/
  main.py
  db.py
  models.py
  schemas.py
  services/
    ingestion.py
    sources/
      base.py
      sample_json_source.py
      provider_stub.py
    prices/
      base.py
      sample_csv_prices.py
    metrics.py
  templates/
  static/

scripts/
  run_ingestion.py

data/
  sample_trades.json
  sample_prices.csv
```
