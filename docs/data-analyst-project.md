# Foundational Data Analyst Projects

Two beginner-level portfolio practice projects apply an analyst workflow to one deterministic, fully fictional dataset:

1. **Retail Sales & Profitability:** data checks, revenue/profit definitions, monthly and category analysis, and a year-filtered dashboard.
2. **Customer Retention Cohorts:** acquisition-month cohorts, specific-month repeat activity, observation windows, and an interactive retention matrix.

The projects include SQL and Python/Pandas exercises and are inspired by foundational learning in data analytics. They are not IBM assignments, IBM-endorsed work, or the IBM capstone.

## Reproduce

From `projects/analytics-foundations/`:

```bash
python python/generate_data.py
python python/analyze.py
python -m http.server 8000
```

Open `http://localhost:8000/dashboard/`. See the [project README](../projects/analytics-foundations/README.md) for metric definitions, project files, and limitations. The dashboard data is synthetic; it must not be described as a real company's performance or as an observed commercial finding.
