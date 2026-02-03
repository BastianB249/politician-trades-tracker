from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import IngestionLog, Politician, Trade
from app.services.metrics import refresh_metrics
from app.services.prices.base import PriceProvider
from app.services.sources.base import RawTrade, TradeSource


def normalize_trade(raw: RawTrade, source: TradeSource) -> dict:
    payload = asdict(raw)
    payload["trade_type"] = payload["trade_type"].upper()
    payload["ticker"] = payload["ticker"].upper()
    payload["source"] = source.source_name
    return payload


def _get_or_create_politician(session: Session, raw: RawTrade) -> Politician:
    politician = session.query(Politician).filter(Politician.name == raw.politician).one_or_none()
    if politician is None:
        politician = Politician(name=raw.politician, chamber=raw.chamber, state=raw.state)
        session.add(politician)
        session.flush()
    return politician


def ingest_trades(
    session: Session,
    sources: list[TradeSource],
    price_provider: PriceProvider,
) -> int:
    added = 0
    for source in sources:
        raw_trades = source.fetch_trades()
        for raw in raw_trades:
            politician = _get_or_create_politician(session, raw)
            normalized = normalize_trade(raw, source)
            trade = Trade(
                politician_id=politician.id,
                trade_date=normalized["trade_date"],
                ticker=normalized["ticker"],
                asset_name=normalized.get("asset_name"),
                trade_type=normalized["trade_type"],
                amount_range=normalized["amount_range"],
                source=normalized["source"],
                source_url=normalized["source_url"],
            )
            session.add(trade)
            try:
                session.commit()
                added += 1
            except IntegrityError:
                session.rollback()
    refresh_metrics(session, price_provider)
    session.add(IngestionLog(trades_added=added, run_at=datetime.utcnow()))
    session.commit()
    return added
