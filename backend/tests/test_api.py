from fastapi.testclient import TestClient

from app.main import app
from app.services.providers import ModoAgrarioScraperProvider

client = TestClient(app)


def test_health_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_latest_quote_ok() -> None:
    response = client.get(
        "/quotes/latest",
        params={"product": "harina_000", "currency": "USD"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["latest_price_per_ton"] == 301.0
    assert payload["day_change_pct"] == 1.35
    assert payload["source"] == "mock_seed"


def test_latest_quote_uses_fallback_mockdata() -> None:
    response = client.get(
        "/quotes/latest",
        params={"product": "harina_0000", "currency": "USD"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["latest_price_per_ton"] == 310.0
    assert payload["source"] == "mock_fallback"


def test_sources_endpoint_lists_integrations() -> None:
    response = client.get("/sources")
    assert response.status_code == 200
    payload = response.json()
    source_names = {item["source"] for item in payload}
    assert "mock_seed" in source_names
    assert "modoagrario_scraper" in source_names


def test_modoagrario_parser_table_sample() -> None:
    html = """
    <table>
      <tr><th>Producto</th><th>Mercado</th><th>Precio</th><th>Fecha</th></tr>
      <tr><td>Harina 000</td><td>Rosario</td><td>USD 320</td><td>2026-02-22</td></tr>
    </table>
    """
    provider = ModoAgrarioScraperProvider()
    data = provider.parse_html(html)

    assert len(data) == 1
    assert data[0].product == "harina_000"
    assert data[0].currency == "USD"
    assert data[0].price_per_ton == 320.0
