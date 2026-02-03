# Capitol Trades Tracker

Capitol Trades Tracker is a FastAPI + SQLite MVP that surfaces US politician stock trade disclosures, complete with computed performance metrics versus SPY.

## Features
- Server-rendered web app with searchable trades and leaderboards.
- Ingestion pipeline supporting multiple sources (sample JSON included).
- Price provider interface with a sample CSV implementation.
- Transparent performance metrics (excess return vs SPY over 1y/5y windows).

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

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run ingestion
```bash
python scripts/run_ingestion.py
```

## Run the server
```bash
python -m uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000` to view the app.

## Tests
```bash
pytest
```
