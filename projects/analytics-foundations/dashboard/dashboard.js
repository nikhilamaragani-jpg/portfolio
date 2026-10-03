const money = new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
const percent = new Intl.NumberFormat("en-IE", { maximumFractionDigits: 1 });

function renderRankChart(element, entries, valueKey, labelKey) {
  const maxValue = Math.max(...entries.map((entry) => entry[valueKey]), 1);
  element.innerHTML = entries
    .sort((a, b) => b[valueKey] - a[valueKey])
    .map((entry) => `
      <div class="rank-row">
        <span>${entry[labelKey]}</span>
        <div class="rank-track" role="img" aria-label="${entry[labelKey]}: ${money.format(entry[valueKey])}">
          <i style="width:${(entry[valueKey] / maxValue) * 100}%"></i>
        </div>
        <strong>${money.format(entry[valueKey])}</strong>
      </div>
    `)
    .join("");
}

function renderMonthlyChart(element, entries) {
  const maxValue = Math.max(...entries.map((entry) => entry.revenue_eur), 1);
  element.innerHTML = entries
    .map((entry) => {
      const height = Math.max(4, (entry.revenue_eur / maxValue) * 100);
      const label = new Date(`${entry.month}-01T00:00:00`).toLocaleString("en", { month: "short" });
      return `<div class="month-bar" tabindex="0" role="img" aria-label="${entry.month}: ${money.format(entry.revenue_eur)} revenue, ${entry.orders} orders" title="${entry.month}: ${money.format(entry.revenue_eur)}">
        <strong>${money.format(entry.revenue_eur)}</strong><i style="height:${height}%"></i><span>${label}</span></div>`;
    })
    .join("");
}

function monthsForYear(data, year) {
  const finalYear = Number(data.metadata.period_end.slice(0, 4));
  const finalMonth = Number(data.metadata.period_end.slice(5, 7));
  const monthLimit = year === finalYear ? finalMonth : 12;
  const indexed = new Map(
    data.monthly.filter((row) => row.year === year).map((row) => [row.month, row])
  );
  return Array.from({ length: monthLimit }, (_, index) => {
    const month = `${year}-${String(index + 1).padStart(2, "0")}`;
    return (
      indexed.get(month) ?? {
        year,
        month,
        revenue_eur: 0,
        gross_profit_eur: 0,
        orders: 0,
        customers: 0,
        average_order_value_eur: 0,
        profit_margin_pct: 0,
      }
    );
  });
}

async function loadDashboard() {
  const response = await fetch("summary.json");
  if (!response.ok) throw new Error(`Could not load dashboard data (${response.status}).`);
  const data = await response.json();
  const filter = document.querySelector("#year-filter");
  const years = [...data.years].sort((a, b) => a.year - b.year);
  const endYear = Number(data.metadata.period_end.slice(0, 4));
  const endMonth = Number(data.metadata.period_end.slice(5, 7));
  filter.innerHTML = years
    .map((row) => {
      const partial = row.year === endYear && endMonth < 12 ? " (partial year)" : "";
      return `<option value="${row.year}">${row.year}${partial}</option>`;
    })
    .join("");
  filter.addEventListener("change", () => renderYear(data, Number(filter.value)));
  document.querySelector("#period-note").textContent =
    `Synthetic dataset · ${data.metadata.period_start} to ${data.metadata.period_end} · ${data.metadata.orders} orders · currency EUR`;
  renderYear(data, years.at(-1).year);
}

function renderYear(data, year) {
  const summary = data.years.find((row) => row.year === year);
  document.querySelector("#revenue").textContent = money.format(summary.revenue_eur);
  document.querySelector("#profit").textContent = money.format(summary.gross_profit_eur);
  document.querySelector("#margin").textContent = `${percent.format(summary.profit_margin_pct)}%`;
  document.querySelector("#aov").textContent = money.format(summary.average_order_value_eur);
  renderMonthlyChart(
    document.querySelector("#monthly-chart"),
    monthsForYear(data, year)
  );
  renderRankChart(
    document.querySelector("#category-chart"),
    data.categories.filter((row) => row.year === year),
    "revenue_eur",
    "product_category"
  );
  renderRankChart(
    document.querySelector("#region-chart"),
    data.regions.filter((row) => row.year === year),
    "revenue_eur",
    "region"
  );
}

loadDashboard().catch((error) => {
  document.querySelector("main").insertAdjacentHTML(
    "afterbegin",
    `<p class="error" role="alert">Dashboard data could not be loaded. Run the project from a local web server and rerun the analysis script. ${error.message}</p>`
  );
});
