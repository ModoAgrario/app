const cardsContainer = document.getElementById("cardsContainer");

const PRICE_ROWS = [
  {
    product: "Harina de Trigo 000",
    presentation: "Bls x 25 Kg.",
    unit: "$/Bls",
    from: 8650,
    to: 9200,
    changePct: 0.82,
    updatedAt: "2026-02-25 15:20",
  },
  {
    product: "Harina de Trigo 000",
    presentation: "Big Bag",
    unit: "$/Tn.",
    from: 299500,
    to: 323000,
    changePct: 0.77,
    updatedAt: "2026-02-25 15:20",
  },
  {
    product: "Harina de Trigo 000",
    presentation: "Granel Tolva",
    unit: "$/Blks",
    from: 284000,
    to: 308500,
    changePct: 0.65,
    updatedAt: "2026-02-25 15:20",
  },
  {
    product: "Harina de Trigo 0000",
    presentation: "Bls x 25 Kg.",
    unit: "$/Bls",
    from: 9250,
    to: 9890,
    changePct: 0.91,
    updatedAt: "2026-02-25 15:20",
  },
  {
    product: "Semolín",
    presentation: "Bls x 25 Kg.",
    unit: "$/Bls",
    from: 10200,
    to: 11050,
    changePct: 0.58,
    updatedAt: "2026-02-25 15:20",
  },
  {
    product: "Salvado",
    presentation: "Bls x 25 Kg.",
    unit: "$/Bls",
    from: 4200,
    to: 4850,
    changePct: 1.2,
    updatedAt: "2026-02-25 15:20",
  },
  {
    product: "Harina Tapera",
    presentation: "Bls x 25 Kg.",
    unit: "$/Bls",
    from: 7300,
    to: 8040,
    changePct: 0.54,
    updatedAt: "2026-02-25 15:20",
  },
];

function money(value) {
  return `$ ${new Intl.NumberFormat("es-AR", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)}`;
}

function cardTemplate(item) {
  return `
    <article class="price-card">
      <h2 class="product">${item.product}</h2>
      <p class="presentation">${item.presentation}</p>
      <p class="unit">${item.unit}</p>

      <div class="metrics">
        <div>
          <p class="metric-label">Desde</p>
          <p class="metric-value">${money(item.from)}</p>
        </div>
        <div>
          <p class="metric-label">Hasta</p>
          <p class="metric-value">${money(item.to)}</p>
        </div>
      </div>

      <p class="var">▲ ${item.changePct.toFixed(2).replace(".", ",")}%</p>
      <p class="updated">Última actualización: ${item.updatedAt}</p>
    </article>
  `;
}

function render() {
  cardsContainer.innerHTML = PRICE_ROWS.map(cardTemplate).join("");
}

window.addEventListener("DOMContentLoaded", render);
