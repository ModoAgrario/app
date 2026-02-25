# API + Frontend MVP - Cotización de Harina de Trigo

Esta base ahora está preparada para:
- servir un frontend mobile-first minimalista,
- consumir cotizaciones de múltiples proveedores,
- y hacer scraping de `ModoAgrario.com/market` de forma desacoplada.

## Stack
- FastAPI + Jinja2 (API + UI)
- Pydantic v2
- httpx (integración APIs/scraping)
- BeautifulSoup4 (parser HTML)

## Estructura clave
- `app/main.py`: API principal + página frontend (`/`).
- `app/services/providers.py`: proveedores de datos (`mock`, `external_api`, `modoagrario_scraper`).
- `app/services/quotes_service.py`: agregador multi-fuente.
- `app/static/*`: estilos y JS frontend.
- `app/templates/index.html`: interfaz tipo dashboard simple.

## Endpoints
- `GET /` frontend minimalista (estilo limpio tipo ChatGPT)
- `GET /health`
- `GET /sources` fuentes habilitadas
- `GET /quotes/latest?product=harina_000&currency=USD`
- `GET /quotes/history?product=harina_000&currency=USD`

## Configuración opcional
Podés conectar otra API externa seteando:
- `EXTERNAL_QUOTES_BASE_URL=https://tu-proveedor.com`

El proveedor esperará `GET /quotes` con JSON compatible:
```json
[
  {
    "market": "Rosario",
    "currency": "USD",
    "product": "harina_000",
    "price_per_ton": 310,
    "collected_at": "2026-02-22"
  }
]
```

## Correr local
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tests
```bash
pip install pytest
PYTHONPATH=. pytest -q
```

## Nota de fallback UI
- El frontend incluye `mockdata` local en `static/app.js` para evitar pantalla en 404 si el endpoint `/quotes/latest` no está disponible en una preview estática.
