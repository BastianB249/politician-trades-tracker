from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from app.services.prices.base import PriceProvider


class SampleCsvPriceProvider(PriceProvider):
    def __init__(self, csv_path: Path) -> None:
        self.csv_path = csv_path
        self._prices: dict[tuple[str, date], float] | None = None

    def _load(self) -> None:
        prices: dict[tuple[str, date], float] = {}
        with self.csv_path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                prices[(row["ticker"].upper(), date.fromisoformat(row["date"]))] = float(row["close"])
        self._prices = prices

    def get_price(self, ticker: str, on_date: date) -> float | None:
        if self._prices is None:
            self._load()
        return self._prices.get((ticker.upper(), on_date))
