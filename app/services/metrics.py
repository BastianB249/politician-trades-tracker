from __future__ import annotations

from collections import Counter
from datetime import date, timedelta, datetime

from sqlalchemy.orm import Session

from app.models import Metrics, Politician, Trade
from app.services.prices.base import PriceProvider


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _calculate_return(price_provider: PriceProvider, ticker: str, start: date, end: date) -> float | None:
    start_price = price_provider.get_price(ticker, start)
    end_price = price_provider.get_price(ticker, end)
    if start_price is None or end_price is None:
        return None
    if start_price == 0:
        return None
    return (end_price - start_price) / start_price


def compute_excess_returns(
    trades: list[Trade],
    price_provider: PriceProvider,
    window_days: int,
) -> float | None:
    returns: list[float] = []
    spy_returns: list[float] = []
    for trade in trades:
        if trade.trade_type != "BUY":
            continue
        end_date = trade.trade_date + timedelta(days=window_days)
        trade_return = _calculate_return(price_provider, trade.ticker, trade.trade_date, end_date)
        spy_return = _calculate_return(price_provider, "SPY", trade.trade_date, end_date)
        if trade_return is None or spy_return is None:
            continue
        returns.append(trade_return)
        spy_returns.append(spy_return)
    avg_return = _average(returns)
    avg_spy = _average(spy_returns)
    if avg_return is None or avg_spy is None:
        return None
    return avg_return - avg_spy


def refresh_metrics(session: Session, price_provider: PriceProvider) -> None:
    politicians = session.query(Politician).all()
    for politician in politicians:
        trades = (
            session.query(Trade)
            .filter(Trade.politician_id == politician.id)
            .order_by(Trade.trade_date.desc())
            .all()
        )
        trade_count = len(trades)
        buy_count = sum(1 for trade in trades if trade.trade_type == "BUY")
        sell_count = sum(1 for trade in trades if trade.trade_type == "SELL")
        ticker_counts = Counter(trade.ticker for trade in trades)
        most_traded = ", ".join([ticker for ticker, _ in ticker_counts.most_common(3)])
        excess_return_1y = compute_excess_returns(trades, price_provider, 365)
        excess_return_5y = compute_excess_returns(trades, price_provider, 365 * 5)

        metrics = (
            session.query(Metrics)
            .filter(Metrics.politician_id == politician.id)
            .one_or_none()
        )
        if metrics is None:
            metrics = Metrics(politician_id=politician.id)
            session.add(metrics)
        metrics.trade_count = trade_count
        metrics.buy_count = buy_count
        metrics.sell_count = sell_count
        metrics.most_traded_tickers = most_traded
        metrics.excess_return_1y = excess_return_1y
        metrics.excess_return_5y = excess_return_5y
        metrics.updated_at = datetime.utcnow()
    session.commit()
