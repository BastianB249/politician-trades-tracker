from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass
class RawTrade:
    politician: str
    chamber: str | None
    state: str | None
    trade_date: date
    ticker: str
    asset_name: str | None
    trade_type: str
    amount_range: str
    source_url: str


class TradeSource(Protocol):
    source_name: str

    def fetch_trades(self) -> list[RawTrade]:
        raise NotImplementedError
