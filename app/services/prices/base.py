from __future__ import annotations

from datetime import date
from typing import Protocol


class PriceProvider(Protocol):
    def get_price(self, ticker: str, on_date: date) -> float | None:
        raise NotImplementedError
