from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import SessionLocal, init_db
from app.models import IngestionLog, Metrics, Politician, Trade
from app.schemas import MetaOut, PoliticianOut, TradeOut

app = FastAPI(title="Capitol Trades Tracker", description="US politician trade disclosures")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.on_event("startup")
def startup() -> None:
    init_db()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    trades = db.query(Trade).order_by(Trade.trade_date.desc()).limit(50).all()
    top_performers = (
        db.query(Politician, Metrics)
        .join(Metrics, Metrics.politician_id == Politician.id)
        .order_by(Metrics.excess_return_5y.desc().nullslast())
        .limit(10)
        .all()
    )
    last_ingestion = db.query(IngestionLog).order_by(IngestionLog.run_at.desc()).first()
    return TEMPLATES.TemplateResponse(
        "home.html",
        {
            "request": request,
            "trades": trades,
            "top_performers": top_performers,
            "last_ingestion": last_ingestion,
        },
    )


@app.get("/politicians/{politician_id}", response_class=HTMLResponse)
def politician_detail(
    politician_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    politician = db.query(Politician).filter(Politician.id == politician_id).one()
    trades = (
        db.query(Trade)
        .filter(Trade.politician_id == politician_id)
        .order_by(Trade.trade_date.desc())
        .all()
    )
    metrics = db.query(Metrics).filter(Metrics.politician_id == politician_id).one_or_none()
    return TEMPLATES.TemplateResponse(
        "politician.html",
        {
            "request": request,
            "politician": politician,
            "trades": trades,
            "metrics": metrics,
        },
    )


@app.get("/about", response_class=HTMLResponse)
def about(request: Request) -> HTMLResponse:
    return TEMPLATES.TemplateResponse("about.html", {"request": request})


@app.get("/api/trades", response_model=list[TradeOut])
def api_trades(
    politician_id: int | None = None,
    ticker: str | None = None,
    trade_type: str | None = Query(None, alias="type"),
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[TradeOut]:
    query = db.query(Trade)
    if politician_id:
        query = query.filter(Trade.politician_id == politician_id)
    if ticker:
        query = query.filter(Trade.ticker == ticker.upper())
    if trade_type:
        query = query.filter(Trade.trade_type == trade_type.upper())
    if date_from:
        query = query.filter(Trade.trade_date >= date_from)
    if date_to:
        query = query.filter(Trade.trade_date <= date_to)
    trades = query.order_by(Trade.trade_date.desc()).offset(offset).limit(limit).all()
    return [TradeOut.model_validate(trade) for trade in trades]


@app.get("/api/politicians", response_model=list[PoliticianOut])
def api_politicians(
    sort: str | None = None,
    db: Session = Depends(get_db),
) -> list[PoliticianOut]:
    sort = sort or "excess_return_5y"
    query = db.query(Politician, Metrics).join(Metrics, Metrics.politician_id == Politician.id)
    if sort == "excess_return_5y":
        query = query.order_by(Metrics.excess_return_5y.desc().nullslast())
    elif sort == "excess_return_1y":
        query = query.order_by(Metrics.excess_return_1y.desc().nullslast())
    results = query.all()
    response: list[PoliticianOut] = []
    for politician, metrics in results:
        response.append(
            PoliticianOut(
                id=politician.id,
                name=politician.name,
                chamber=politician.chamber,
                state=politician.state,
                trade_count=metrics.trade_count,
                buy_count=metrics.buy_count,
                sell_count=metrics.sell_count,
                most_traded_tickers=metrics.most_traded_tickers,
                excess_return_1y=metrics.excess_return_1y,
                excess_return_5y=metrics.excess_return_5y,
            )
        )
    return response


@app.get("/api/politicians/{politician_id}", response_model=PoliticianOut)
def api_politician(politician_id: int, db: Session = Depends(get_db)) -> PoliticianOut:
    politician = db.query(Politician).filter(Politician.id == politician_id).one()
    metrics = db.query(Metrics).filter(Metrics.politician_id == politician_id).one_or_none()
    return PoliticianOut(
        id=politician.id,
        name=politician.name,
        chamber=politician.chamber,
        state=politician.state,
        trade_count=metrics.trade_count if metrics else None,
        buy_count=metrics.buy_count if metrics else None,
        sell_count=metrics.sell_count if metrics else None,
        most_traded_tickers=metrics.most_traded_tickers if metrics else None,
        excess_return_1y=metrics.excess_return_1y if metrics else None,
        excess_return_5y=metrics.excess_return_5y if metrics else None,
    )


@app.get("/api/meta", response_model=MetaOut)
def api_meta(db: Session = Depends(get_db)) -> MetaOut:
    last_ingestion = db.query(IngestionLog).order_by(IngestionLog.run_at.desc()).first()
    trade_count = db.query(func.count(Trade.id)).scalar() or 0
    return MetaOut(
        last_ingestion_time=last_ingestion.run_at if last_ingestion else None,
        number_of_trades=trade_count,
    )
