from __future__ import annotations

from app.services.sources.base import RawTrade, TradeSource


class ProviderStub(TradeSource):
    source_name = "future_provider"

    def fetch_trades(self) -> list[RawTrade]:
        return []
