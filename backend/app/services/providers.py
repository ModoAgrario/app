from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Literal, Protocol

import httpx
from bs4 import BeautifulSoup

ProductType = Literal["harina_000", "harina_0000", "harina_integral"]
CurrencyType = Literal["ARS", "USD"]


@dataclass(slots=True)
class QuoteRecord:
    market: str
    currency: CurrencyType
    product: ProductType
    price_per_ton: float
    collected_at: date
    source: str


class QuoteProvider(Protocol):
    source_name: str

    def fetch_quotes(self) -> list[QuoteRecord]:
        ...


class MockQuoteProvider:
    source_name = "mock_seed"

    def fetch_quotes(self) -> list[QuoteRecord]:
        return [
            QuoteRecord(
                market="Rosario",
                currency="USD",
                product="harina_000",
                price_per_ton=290.0,
                collected_at=date(2026, 2, 20),
                source=self.source_name,
            ),
            QuoteRecord(
                market="Rosario",
                currency="USD",
                product="harina_000",
                price_per_ton=297.0,
                collected_at=date(2026, 2, 21),
                source=self.source_name,
            ),
            QuoteRecord(
                market="Rosario",
                currency="USD",
                product="harina_000",
                price_per_ton=301.0,
                collected_at=date(2026, 2, 22),
                source=self.source_name,
            ),
            QuoteRecord(
                market="Buenos Aires",
                currency="ARS",
                product="harina_integral",
                price_per_ton=321000.0,
                collected_at=date(2026, 2, 22),
                source=self.source_name,
            ),
        ]


class ExternalApiQuoteProvider:
    """Provider genérico para integrar APIs de terceros.

    Espera un endpoint JSON con lista de objetos que puedan mapearse a QuoteRecord.
    """

    source_name = "external_api"

    def __init__(self, base_url: str, timeout_s: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    def fetch_quotes(self) -> list[QuoteRecord]:
        try:
            response = httpx.get(f"{self.base_url}/quotes", timeout=self.timeout_s)
            response.raise_for_status()
        except httpx.HTTPError:
            return []

        payload = response.json()
        output: list[QuoteRecord] = []
        for item in payload:
            try:
                output.append(
                    QuoteRecord(
                        market=item["market"],
                        currency=item["currency"],
                        product=item["product"],
                        price_per_ton=float(item["price_per_ton"]),
                        collected_at=date.fromisoformat(item["collected_at"]),
                        source=self.source_name,
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue

        return output


class ModoAgrarioScraperProvider:
    """Scraper preparado para ModoAgrario market.

    Nota: el parser es tolerante y busca estructuras comunes de tablas/cards.
    """

    source_name = "modoagrario_scraper"

    def __init__(self, url: str = "https://modoagrario.com/market", timeout_s: float = 8.0) -> None:
        self.url = url
        self.timeout_s = timeout_s

    def fetch_quotes(self) -> list[QuoteRecord]:
        try:
            response = httpx.get(self.url, timeout=self.timeout_s)
            response.raise_for_status()
        except httpx.HTTPError:
            return []
        return self.parse_html(response.text)

    def parse_html(self, html: str) -> list[QuoteRecord]:
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table tr")
        parsed = self._parse_table_rows(rows)
        if parsed:
            return parsed

        cards = soup.select("[data-product], .market-card")
        return self._parse_cards(cards)

    def _parse_table_rows(self, rows: Iterable) -> list[QuoteRecord]:
        quotes: list[QuoteRecord] = []
        for row in rows:
            cols = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
            if len(cols) < 4:
                continue

            product = self._normalize_product(cols[0])
            if not product:
                continue

            market = cols[1]
            currency, price = self._extract_currency_price(cols[2])
            collected = self._parse_date(cols[3])
            if not currency or price is None:
                continue

            quotes.append(
                QuoteRecord(
                    market=market,
                    currency=currency,
                    product=product,
                    price_per_ton=price,
                    collected_at=collected,
                    source=self.source_name,
                )
            )
        return quotes

    def _parse_cards(self, cards: Iterable) -> list[QuoteRecord]:
        quotes: list[QuoteRecord] = []
        for card in cards:
            text = card.get_text(" ", strip=True)
            product = self._normalize_product(text)
            if not product:
                continue
            currency, price = self._extract_currency_price(text)
            if not currency or price is None:
                continue

            market = card.get("data-market", "ModoAgrario")
            quotes.append(
                QuoteRecord(
                    market=market,
                    currency=currency,
                    product=product,
                    price_per_ton=price,
                    collected_at=date.today(),
                    source=self.source_name,
                )
            )
        return quotes

    @staticmethod
    def _normalize_product(raw: str) -> ProductType | None:
        value = raw.lower()
        if "0000" in value:
            return "harina_0000"
        if "integral" in value:
            return "harina_integral"
        if "000" in value or "trigo" in value:
            return "harina_000"
        return None

    @staticmethod
    def _extract_currency_price(raw: str) -> tuple[CurrencyType | None, float | None]:
        normalized = raw.replace(" ", "")
        currency: CurrencyType | None = None
        if "usd" in normalized.lower() or "$u" in normalized.lower():
            currency = "USD"
        elif "ars" in normalized.lower() or "$" in normalized:
            currency = "ARS"

        clean = "".join(ch for ch in normalized if ch.isdigit() or ch in [",", "."])
        if not clean:
            return currency, None

        if clean.count(",") > 0 and clean.count(".") > 0:
            clean = clean.replace(".", "").replace(",", ".")
        elif clean.count(",") == 1 and clean.count(".") == 0:
            clean = clean.replace(",", ".")

        try:
            return currency, float(clean)
        except ValueError:
            return currency, None

    @staticmethod
    def _parse_date(raw: str) -> date:
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return date.today()
