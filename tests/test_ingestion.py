from __future__ import annotations

from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import Trade
from app.services.ingestion import ingest_trades, normalize_trade
from app.services.prices.base import PriceProvider
from app.services.sources.base import RawTrade, TradeSource


class DummySource(TradeSource):
    source_name = "dummy"

    def __init__(self, trades: list[RawTrade]) -> None:
        self._trades = trades

    def fetch_trades(self) -> list[RawTrade]:
        return self._trades


class DummyPriceProvider(PriceProvider):
    def get_price(self, ticker: str, on_date: date) -> float | None:
        return 100.0


def create_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_normalize_trade() -> None:
    raw = RawTrade(
        politician="Rep. Test",
        chamber="House",
        state="CA",
        trade_date=date(2020, 1, 1),
        ticker="aapl",
        asset_name="Apple",
        trade_type="buy",
        amount_range="$1,001 - $15,000",
        source_url="https://example.com",
    )
    normalized = normalize_trade(raw, DummySource([]))
    assert normalized["trade_type"] == "BUY"
    assert normalized["ticker"] == "AAPL"
    assert normalized["source"] == "dummy"


def test_deduplication() -> None:
    session = create_session()
    trades = [
        RawTrade(
            politician="Rep. Test",
            chamber="House",
            state="CA",
            trade_date=date(2020, 1, 1),
            ticker="AAPL",
            asset_name="Apple",
            trade_type="BUY",
            amount_range="$1,001 - $15,000",
            source_url="https://example.com",
        ),
        RawTrade(
            politician="Rep. Test",
            chamber="House",
            state="CA",
            trade_date=date(2020, 1, 1),
            ticker="AAPL",
            asset_name="Apple",
            trade_type="BUY",
            amount_range="$1,001 - $15,000",
            source_url="https://example.com",
        ),
    ]
    added = ingest_trades(session, [DummySource(trades)], DummyPriceProvider())
    assert added == 1
    assert session.query(Trade).count() == 1
