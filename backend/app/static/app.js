const refreshBtn = document.getElementById("refreshBtn");
const productEl = document.getElementById("product");
const currencyEl = document.getElementById("currency");

const priceEl = document.getElementById("price");
const changeEl = document.getElementById("change");
const metaEl = document.getElementById("meta");

const MOCK_QUOTES = {
  "harina_000-USD": [290.0, 297.0, 301.0],
  "harina_0000-USD": [305.0, 307.0, 310.0],
  "harina_integral-ARS": [315000.0, 319500.0, 321000.0],
  "harina_000-ARS": [280000.0, 286000.0, 289500.0],
};

function formatMoney(value, currency) {
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency,
    maximumFractionDigits: currency === "ARS" ? 0 : 2,
  }).format(value);
}

function getMockSummary(product, currency) {
  const key = `${product}-${currency}`;
  const series = MOCK_QUOTES[key];
  if (!series || series.length === 0) {
    return null;
  }

  const latest = series[series.length - 1];
  const previous = series.length > 1 ? series[series.length - 2] : latest;
  const dayChangePct = previous === 0 ? 0 : ((latest - previous) / previous) * 100;

  return {
    latest_price_per_ton: latest,
    day_change_pct: Number(dayChangePct.toFixed(2)),
    currency,
    source: "mock_frontend",
  };
}

function renderQuote(data) {
  priceEl.textContent = `${formatMoney(data.latest_price_per_ton, data.currency)} / tn`;
  changeEl.textContent = `Variación diaria: ${data.day_change_pct}%`;
  metaEl.textContent = `Fuente: ${data.source}`;
}

async function loadQuote() {
  const product = productEl.value;
  const currency = currencyEl.value;

  try {
    const response = await fetch(`/quotes/latest?product=${product}&currency=${currency}`);
    if (response.ok) {
      const data = await response.json();
      renderQuote(data);
      return;
    }
  } catch (_error) {
    // Si no está disponible la API, hacemos fallback a mockdata local.
  }

  const mockData = getMockSummary(product, currency);
  if (mockData) {
    renderQuote(mockData);
  } else {
    priceEl.textContent = "Sin datos";
    changeEl.textContent = "Variación diaria: --";
    metaEl.textContent = "Fuente: --";
  }
}

refreshBtn.addEventListener("click", loadQuote);
window.addEventListener("DOMContentLoaded", loadQuote);
