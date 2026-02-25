from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.services.quotes_service import ProvidersConfig, QuoteAggregatorService

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Harina Quote API",
    version="0.2.0",
    description="API y frontend MVP para cotización de harina de trigo (mobile-first).",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))



FALLBACK_SERIES: dict[tuple[str, str], list[float]] = {
    ("harina_000", "USD"): [290.0, 297.0, 301.0],
    ("harina_0000", "USD"): [305.0, 307.0, 310.0],
    ("harina_integral", "ARS"): [315000.0, 319500.0, 321000.0],
    ("harina_000", "ARS"): [280000.0, 286000.0, 289500.0],
}


def fallback_quotes(product: str, currency: str) -> list[Quote]:
    values = FALLBACK_SERIES.get((product, currency), [])
    today = date.today()
    return [
        Quote(
            market="MockMarket",
            currency=currency,
            product=product,
            price_per_ton=value,
            collected_at=today - timedelta(days=(len(values) - idx - 1)),
            source="mock_fallback",
        )
        for idx, value in enumerate(values)
    ]


class Quote(BaseModel):
    market: str = Field(description="Mercado o plaza de referencia")
    currency: Literal["ARS", "USD"]
    product: Literal["harina_000", "harina_0000", "harina_integral"]
    price_per_ton: float = Field(gt=0, description="Precio por tonelada")
    collected_at: date
    source: str = Field(description="Proveedor de datos")


class QuoteSummary(BaseModel):
    product: str
    currency: str
    latest_price_per_ton: float
    day_change_pct: float
    source: str


class SourceStatus(BaseModel):
    source: str
    enabled: bool


def get_quote_service() -> QuoteAggregatorService:
    external_api_url = os.getenv("EXTERNAL_QUOTES_BASE_URL")
    config = ProvidersConfig(
        include_mock=True,
        external_api_base_url=external_api_url,
        enable_modoagrario_scraper=True,
    )
    return QuoteAggregatorService.from_config(config)


@app.get("/", response_class=HTMLResponse)
def landing(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Harina Quote"},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/sources", response_model=list[SourceStatus])
def sources_status() -> list[SourceStatus]:
    service = get_quote_service()
    return [SourceStatus(source=provider.source_name, enabled=True) for provider in service.providers]


@app.get("/quotes/latest", response_model=QuoteSummary)
def latest_quote(
    product: Literal["harina_000", "harina_0000", "harina_integral"],
    currency: Literal["ARS", "USD"] = Query(...),
) -> QuoteSummary:
    service = get_quote_service()
    quotes = service.filter_quotes(product=product, currency=currency)

    if not quotes:
        fallback = fallback_quotes(product, currency)
        if fallback:
            quotes = sorted(fallback, key=lambda x: x.collected_at, reverse=True)
        else:
            raise HTTPException(status_code=404, detail="No hay cotizaciones para ese filtro")

    latest = quotes[0]

    if len(quotes) == 1:
        day_change_pct = 0.0
    else:
        previous = quotes[1]
        day_change_pct = ((latest.price_per_ton - previous.price_per_ton) / previous.price_per_ton) * 100

    return QuoteSummary(
        product=latest.product,
        currency=latest.currency,
        latest_price_per_ton=latest.price_per_ton,
        day_change_pct=round(day_change_pct, 2),
        source=latest.source,
    )


@app.get("/quotes/history", response_model=list[Quote])
def quote_history(
    product: Literal["harina_000", "harina_0000", "harina_integral"],
    currency: Literal["ARS", "USD"],
) -> list[Quote]:
    service = get_quote_service()
    quotes = service.filter_quotes(product=product, currency=currency)
    if not quotes:
        quotes = fallback_quotes(product, currency)
        if not quotes:
            raise HTTPException(status_code=404, detail="Sin histórico para ese filtro")

    return [
        Quote(
            market=q.market,
            currency=q.currency,
            product=q.product,
            price_per_ton=q.price_per_ton,
            collected_at=q.collected_at,
            source=q.source,
        )
        for q in quotes
    ]
