# Retail Analytics Foundations

Two beginner-level Data Analyst portfolio practice case studies using one reproducible, fully synthetic retail dataset:

1. [Retail Sales & Profitability dashboard](dashboard/index.html) — monthly revenue, gross profit, margin, average order value, product mix, and region.
2. [Customer Retention Cohorts dashboard](dashboard/retention.html) — acquisition-month cohorts and observed month-by-month return activity.

These projects practice a foundational analytics workflow—define questions, validate data, calculate measures, query, visualize, and explain limitations. They are **inspired by introductory analytics learning**, not an IBM assignment, IBM-endorsed project, or course capstone.

Before presenting these as personal work in an interview, run the project yourself, inspect the generator and analysis, recreate key SQL/Python calculations, and be ready to explain the assumptions and limitations.

## Dataset

`data/retail_orders.csv` contains generated fictional transactions in EUR for 240 fictional customer IDs. It is generated deterministically using Python's standard library and seed `20261003`; the generator creates acquisition-month cohorts, repeat-order behavior, discounts, product costs, regions, channels, and seasonal pricing effects. It contains no real company or customer data.

## Reproduce the analysis

From this directory:

```bash
python python/generate_data.py
python -m pip install pandas
python python/analyze.py
python -m http.server 8000
```

Open `http://localhost:8000/dashboard/`. The dashboards load the generated `dashboard/summary.json`, so use a local HTTP server rather than opening the HTML files directly. The included summary JSON is precomputed for convenience.

## Project contents

- `data/retail_orders.csv` — generated dataset
- `python/generate_data.py` — deterministic data generator
- `python/analyze.py` — data-quality validation, derived KPIs, and dashboard summary export
- `sql/analysis.sql` — SQLite data checks, KPI, category, repeat-purchase, and cohort queries
- `dashboard/` — responsive HTML dashboards with year selection and a cohort matrix
- `powerbi/measures.dax` — starter Power BI measures for a possible imported model
- `powerbi/dashboard-spec.md` — layout and metric definitions for recreating the report in Power BI

## Metric definitions

- **Revenue:** units × unit price × (1 − discount rate), summed before rounding reported results to cents
- **Cost:** units × unit cost
- **Gross profit:** revenue − cost
- **Gross margin:** gross profit ÷ revenue
- **Average order value:** revenue ÷ distinct orders
- **Repeat customer rate:** customers with more than one distinct order ÷ all distinct customers
- **Cohort retention at month N:** distinct customers in that cohort with at least one order in elapsed calendar month N ÷ original cohort size. This is period-specific, not cumulative.

## Limitations

The data generator deliberately creates the patterns being analyzed; visual trends and rates are demonstrations of analytical methods, not discoveries about a real retailer. The dataset is small and fictional. It does not establish causal impact or support external business decisions. Compare cohorts only over elapsed months observed for each cohort.

## Power BI

The HTML dashboard is a working web-based portfolio dashboard, not a `.pbix` file. Use the CSV and included DAX measure and layout notes to recreate the model in Power BI Desktop. The original workshop dashboards are separate; their PDF is in `../../assets/powerbi-dashboards.pdf`.
