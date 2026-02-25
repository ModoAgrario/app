from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .providers import (
    CurrencyType,
    ExternalApiQuoteProvider,
    MockQuoteProvider,
    ModoAgrarioScraperProvider,
    ProductType,
    QuoteProvider,
    QuoteRecord,
)


@dataclass(slots=True)
class ProvidersConfig:
    include_mock: bool = True
    external_api_base_url: str | None = None
    enable_modoagrario_scraper: bool = True


class QuoteAggregatorService:
    def __init__(self, providers: Iterable[QuoteProvider]) -> None:
        self.providers = list(providers)

    @classmethod
    def from_config(cls, config: ProvidersConfig) -> "QuoteAggregatorService":
        providers: list[QuoteProvider] = []
        if config.include_mock:
            providers.append(MockQuoteProvider())

        if config.external_api_base_url:
            providers.append(ExternalApiQuoteProvider(config.external_api_base_url))

        if config.enable_modoagrario_scraper:
            providers.append(ModoAgrarioScraperProvider())

        return cls(providers)

    def all_quotes(self) -> list[QuoteRecord]:
        output: list[QuoteRecord] = []
        for provider in self.providers:
            output.extend(provider.fetch_quotes())
        return output

    def filter_quotes(self, product: ProductType, currency: CurrencyType) -> list[QuoteRecord]:
        filtered = [q for q in self.all_quotes() if q.product == product and q.currency == currency]
        return sorted(filtered, key=lambda x: x.collected_at, reverse=True)
