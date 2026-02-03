from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from app.db import SessionLocal, init_db
from app.services.ingestion import ingest_trades
from app.services.prices.sample_csv_prices import SampleCsvPriceProvider
from app.services.sources.sample_json_source import SampleJsonSource
from app.services.sources.provider_stub import ProviderStub


def main() -> None:
    init_db()
    session = SessionLocal()
    sources = [
        SampleJsonSource(BASE_DIR / "data" / "sample_trades.json"),
        ProviderStub(),
    ]
    price_provider = SampleCsvPriceProvider(BASE_DIR / "data" / "sample_prices.csv")
    added = ingest_trades(session, sources, price_provider)
    session.close()
    print(f"Ingestion complete. Added {added} new trades.")


if __name__ == "__main__":
    main()
