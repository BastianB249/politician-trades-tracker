from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from app.services.sources.base import RawTrade


class SampleJsonSource:
    source_name = "sample_json"

    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path

    def fetch_trades(self) -> list[RawTrade]:
        payload = json.loads(self.data_path.read_text())
        trades: list[RawTrade] = []
        for entry in payload:
            trades.append(
                RawTrade(
                    politician=entry["politician"],
                    chamber=entry.get("chamber"),
                    state=entry.get("state"),
                    trade_date=date.fromisoformat(entry["trade_date"]),
                    ticker=entry["ticker"].upper(),
                    asset_name=entry.get("asset_name"),
                    trade_type=entry["type"].upper(),
                    amount_range=entry["amount_range"],
                    source_url=entry["source_url"],
                )
            )
        return trades
