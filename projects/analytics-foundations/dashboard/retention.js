const number = new Intl.NumberFormat("en");
const pct = new Intl.NumberFormat("en", { maximumFractionDigits: 1 });

async function loadRetention() {
  const response = await fetch("summary.json");
  if (!response.ok) throw new Error(`Could not load cohort data (${response.status}).`);
  const data = await response.json();
  const cohortRows = data.cohorts;
  const repeat = data.overall;
  const weightedMonthOne = cohortRows.reduce(
    (acc, cohort) => {
      if (cohort.retained_customers.length > 1) {
        acc.retained += cohort.retained_customers[1];
        acc.size += cohort.size;
      }
      return acc;
    },
    { retained: 0, size: 0 }
  );
  document.querySelector("#customers").textContent = number.format(repeat.customers);
  document.querySelector("#repeat-customers").textContent = number.format(repeat.repeat_customers);
  document.querySelector("#repeat-rate").textContent = `${pct.format(repeat.repeat_customer_rate_pct)}%`;
  document.querySelector("#month-one").textContent = weightedMonthOne.size
    ? `${pct.format((weightedMonthOne.retained / weightedMonthOne.size) * 100)}%`
    : "—";
  document.querySelector("#cohort-period").textContent =
    `Synthetic dataset · ${data.metadata.period_start} to ${data.metadata.period_end} · acquisition cohorts by calendar month`;
  renderCohorts(cohortRows);
}

function renderCohorts(cohorts) {
  const maxMonths = Math.max(...cohorts.map((cohort) => cohort.retention_pct.length));
  const table = document.querySelector("#cohort-table");
  table.querySelector("thead").innerHTML = `<tr><th scope="col">Cohort</th><th scope="col">Size</th>${Array.from(
    { length: maxMonths },
    (_, index) => `<th scope="col">M${index}</th>`
  ).join("")}</tr>`;
  table.querySelector("tbody").innerHTML = cohorts
    .map(
      (cohort) => `<tr>
        <th scope="row">${cohort.cohort}</th><td>${number.format(cohort.size)}</td>
        ${Array.from({ length: maxMonths }, (_, index) => {
          const value = cohort.retention_pct[index];
          if (value === undefined) return "<td class=\"not-observed\">—</td>";
          const alpha = 0.08 + (value / 100) * 0.78;
          const customers = cohort.retained_customers[index];
          return `<td style="--heat:${alpha}" aria-label="${pct.format(value)} percent; ${customers} of ${cohort.size} customers">${pct.format(value)}%<small>${customers}/${cohort.size}</small></td>`;
        }).join("")}
      </tr>`
    )
    .join("");
}

loadRetention().catch((error) => {
  document.querySelector("main").insertAdjacentHTML(
    "afterbegin",
    `<p class="error" role="alert">Cohort data could not be loaded. Run the project from a local web server and rerun the analysis script. ${error.message}</p>`
  );
});
