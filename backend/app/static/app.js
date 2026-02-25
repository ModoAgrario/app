const refreshBtn = document.getElementById("refreshBtn");
const productEl = document.getElementById("product");
const currencyEl = document.getElementById("currency");

const priceEl = document.getElementById("price");
const changeEl = document.getElementById("change");
const metaEl = document.getElementById("meta");

function formatMoney(value, currency) {
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency,
    maximumFractionDigits: currency === "ARS" ? 0 : 2,
  }).format(value);
}

async function loadQuote() {
  const product = productEl.value;
  const currency = currencyEl.value;

  try {
    const response = await fetch(`/quotes/latest?product=${product}&currency=${currency}`);
    if (!response.ok) {
      throw new Error("No hay datos para ese filtro");
    }

    const data = await response.json();
    priceEl.textContent = `${formatMoney(data.latest_price_per_ton, data.currency)} / tn`;
    changeEl.textContent = `Variación diaria: ${data.day_change_pct}%`;
    metaEl.textContent = `Fuente: ${data.source}`;
  } catch (error) {
    priceEl.textContent = "Sin datos";
    changeEl.textContent = "Variación diaria: --";
    metaEl.textContent = "Fuente: --";
  }
}

refreshBtn.addEventListener("click", loadQuote);
window.addEventListener("DOMContentLoaded", loadQuote);
