from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Politician(Base):
    __tablename__ = "politicians"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    chamber: Mapped[str | None] = mapped_column(String(50))
    state: Mapped[str | None] = mapped_column(String(10))

    trades: Mapped[list[Trade]] = relationship("Trade", back_populates="politician")
    metrics: Mapped[Metrics | None] = relationship("Metrics", back_populates="politician", uselist=False)


class Trade(Base):
    __tablename__ = "trades"
    __table_args__ = (
        UniqueConstraint(
            "politician_id",
            "trade_date",
            "ticker",
            "trade_type",
            "amount_range",
            "source_url",
            name="uq_trade_dedup",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    politician_id: Mapped[int] = mapped_column(ForeignKey("politicians.id"), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    asset_name: Mapped[str | None] = mapped_column(String(200))
    trade_type: Mapped[str] = mapped_column(String(20), index=True)
    amount_range: Mapped[str] = mapped_column(String(50))
    source: Mapped[str] = mapped_column(String(50))
    source_url: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    politician: Mapped[Politician] = relationship("Politician", back_populates="trades")


class Metrics(Base):
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    politician_id: Mapped[int] = mapped_column(ForeignKey("politicians.id"), unique=True)
    trade_count: Mapped[int] = mapped_column(Integer, default=0)
    buy_count: Mapped[int] = mapped_column(Integer, default=0)
    sell_count: Mapped[int] = mapped_column(Integer, default=0)
    most_traded_tickers: Mapped[str] = mapped_column(String(200), default="")
    excess_return_1y: Mapped[float | None] = mapped_column(Float)
    excess_return_5y: Mapped[float | None] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    politician: Mapped[Politician] = relationship("Politician", back_populates="metrics")


class IngestionLog(Base):
    __tablename__ = "ingestion_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    trades_added: Mapped[int] = mapped_column(Integer, default=0)
