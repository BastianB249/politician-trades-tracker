from __future__ import annotations

from datetime import date
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import Politician, Trade
from app.services.ingestion import ingest_trades
from app.services.metrics import compute_excess_returns, refresh_metrics
from app.services.prices.base import PriceProvider
from app.services.prices.sample_csv_prices import SampleCsvPriceProvider
from app.services.sources.sample_json_source import SampleJsonSource


class DictPriceProvider(PriceProvider):
    def __init__(self, data: dict[tuple[str, date], float]) -> None:
        self.data = data

    def get_price(self, ticker: str, on_date: date) -> float | None:
        return self.data.get((ticker, on_date))


def create_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_compute_excess_returns() -> None:
    provider = DictPriceProvider(
        {
            ("ABC", date(2020, 1, 1)): 100,
            ("ABC", date(2021, 1, 1)): 120,
            ("SPY", date(2020, 1, 1)): 200,
            ("SPY", date(2021, 1, 1)): 210,
        }
    )
    trade = Trade(
        politician_id=1,
        trade_date=date(2020, 1, 1),
        ticker="ABC",
        asset_name="ABC",
        trade_type="BUY",
        amount_range="$1,001 - $15,000",
        source="dummy",
        source_url="https://example.com",
    )
    excess = compute_excess_returns([trade], provider, 365)
    assert round(excess or 0, 4) == 0.15


def test_refresh_metrics() -> None:
    session = create_session()
    politician = Politician(name="Rep. Test", chamber="House", state="CA")
    session.add(politician)
    session.commit()
    trade = Trade(
        politician_id=politician.id,
        trade_date=date(2020, 1, 1),
        ticker="ABC",
        asset_name="ABC",
        trade_type="BUY",
        amount_range="$1,001 - $15,000",
        source="dummy",
        source_url="https://example.com",
    )
    session.add(trade)
    session.commit()

    provider = DictPriceProvider(
        {
            ("ABC", date(2020, 1, 1)): 100,
            ("ABC", date(2021, 1, 1)): 120,
            ("SPY", date(2020, 1, 1)): 200,
            ("SPY", date(2021, 1, 1)): 210,
            ("ABC", date(2025, 1, 1)): 150,
            ("SPY", date(2025, 1, 1)): 250,
        }
    )
    refresh_metrics(session, provider)
    metrics = politician.metrics
    assert metrics is not None
    assert metrics.trade_count == 1
    assert metrics.buy_count == 1
    assert metrics.sell_count == 0


def test_sample_metrics_have_non_zero_returns() -> None:
    session = create_session()
    base_dir = Path(__file__).resolve().parents[1]
    trades_source = SampleJsonSource(base_dir / "data" / "sample_trades.json")
    price_provider = SampleCsvPriceProvider(base_dir / "data" / "sample_prices.csv")

    ingest_trades(session, [trades_source], price_provider)

    metrics_values = [
        politician.metrics.excess_return_5y
        for politician in session.query(Politician).all()
        if politician.metrics is not None
    ]
    assert any(value is not None and abs(value) > 0.001 for value in metrics_values)
