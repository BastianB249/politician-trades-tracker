from __future__ import annotations

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class TradeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    politician_id: int
    trade_date: date
    ticker: str
    asset_name: str | None
    trade_type: str
    amount_range: str
    source: str
    source_url: str
    created_at: datetime


class PoliticianOut(BaseModel):
    id: int
    name: str
    chamber: str | None
    state: str | None
    trade_count: int | None = None
    buy_count: int | None = None
    sell_count: int | None = None
    most_traded_tickers: str | None = None
    excess_return_1y: float | None = None
    excess_return_5y: float | None = None
    top_tickers: list[str] | None = None
    metrics_summary: dict[str, float | int | None] | None = None


class MetaOut(BaseModel):
    last_ingestion_time: datetime | None
    number_of_trades: int
