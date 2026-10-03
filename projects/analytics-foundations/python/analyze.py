"""Validate synthetic retail data and prepare data for the portfolio dashboards."""

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "retail_orders.csv"
SUMMARY_PATH = PROJECT_ROOT / "dashboard" / "summary.json"
REQUIRED_COLUMNS = {
    "order_id",
    "order_date",
    "customer_id",
    "acquisition_date",
    "region",
    "channel",
    "product_category",
    "units",
    "unit_price_eur",
    "unit_cost_eur",
    "discount_rate",
}


def main() -> None:
    orders = pd.read_csv(DATA_PATH, parse_dates=["order_date", "acquisition_date"])
    missing_columns = REQUIRED_COLUMNS - set(orders.columns)
    if missing_columns:
        raise ValueError(f"Required columns are missing: {sorted(missing_columns)}")
    if orders[list(REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError("Dataset contains missing values in required fields.")
    if orders["order_id"].duplicated().any():
        raise ValueError("order_id must be unique.")
    if (orders["units"] <= 0).any():
        raise ValueError("units must be greater than zero.")
    if (orders["discount_rate"].lt(0) | orders["discount_rate"].ge(1)).any():
        raise ValueError("discount_rate must be between zero (inclusive) and one (exclusive).")
    if (orders["order_date"] < orders["acquisition_date"]).any():
        raise ValueError("An order cannot occur before the customer's acquisition date.")

    orders["revenue_eur"] = (
        orders["units"] * orders["unit_price_eur"] * (1 - orders["discount_rate"])
    )
    orders["cost_eur"] = orders["units"] * orders["unit_cost_eur"]
    orders["gross_profit_eur"] = orders["revenue_eur"] - orders["cost_eur"]
    orders["year"] = orders["order_date"].dt.year
    orders["month"] = orders["order_date"].dt.strftime("%Y-%m")
    orders["cohort"] = orders["acquisition_date"].dt.strftime("%Y-%m")
    order_month_index = orders["order_date"].dt.year * 12 + orders["order_date"].dt.month
    cohort_month_index = orders["acquisition_date"].dt.year * 12 + orders["acquisition_date"].dt.month
    orders["months_since_acquisition"] = order_month_index - cohort_month_index

    def summarize(frame: pd.DataFrame, keys: list[str]) -> list[dict]:
        result = (
            frame.groupby(keys, dropna=False)
            .agg(
                orders=("order_id", "nunique"),
                customers=("customer_id", "nunique"),
                revenue_eur=("revenue_eur", "sum"),
                gross_profit_eur=("gross_profit_eur", "sum"),
            )
            .reset_index()
        )
        result["average_order_value_eur"] = result["revenue_eur"] / result["orders"]
        result["profit_margin_pct"] = (
            result["gross_profit_eur"] / result["revenue_eur"] * 100
        )
        result = result.round(
            {
                "revenue_eur": 2,
                "gross_profit_eur": 2,
                "average_order_value_eur": 2,
                "profit_margin_pct": 2,
            }
        )
        return result.to_dict(orient="records")

    customer_orders = orders.groupby("customer_id")["order_id"].nunique()
    overall_revenue = float(orders["revenue_eur"].sum())
    overall_profit = float(orders["gross_profit_eur"].sum())
    overall_customers = int(orders["customer_id"].nunique())
    repeat_customers = int((customer_orders > 1).sum())

    cohort_sizes = (
        orders[["customer_id", "cohort"]]
        .drop_duplicates()
        .groupby("cohort")["customer_id"]
        .nunique()
    )
    cohort_rows = []
    for cohort, cohort_frame in orders.groupby("cohort"):
        size = int(cohort_sizes.loc[cohort])
        retention = []
        retained = []
        for month_index in range(int(cohort_frame["months_since_acquisition"].max()) + 1):
            customers = int(
                cohort_frame.loc[
                    cohort_frame["months_since_acquisition"] == month_index, "customer_id"
                ].nunique()
            )
            retained.append(customers)
            retention.append(round(customers / size * 100, 1) if size else None)
        cohort_rows.append(
            {
                "cohort": cohort,
                "size": size,
                "retained_customers": retained,
                "retention_pct": retention,
            }
        )

    years = []
    for year, frame in orders.groupby("year"):
        year_customers = frame.groupby("customer_id")["order_id"].nunique()
        revenue = float(frame["revenue_eur"].sum())
        profit = float(frame["gross_profit_eur"].sum())
        years.append(
            {
                "year": int(year),
                "orders": int(frame["order_id"].nunique()),
                "customers": int(frame["customer_id"].nunique()),
                "revenue_eur": round(revenue, 2),
                "gross_profit_eur": round(profit, 2),
                "average_order_value_eur": round(revenue / frame["order_id"].nunique(), 2),
                "profit_margin_pct": round(profit / revenue * 100, 2),
                "repeat_customer_rate_pct": round(int((year_customers > 1).sum()) / frame["customer_id"].nunique() * 100, 2),
            }
        )

    summary = {
        "metadata": {
            "data_type": "synthetic",
            "currency": "EUR",
            "period_start": orders["order_date"].min().strftime("%Y-%m-%d"),
            "period_end": orders["order_date"].max().strftime("%Y-%m-%d"),
            "orders": int(orders["order_id"].nunique()),
            "customers": overall_customers,
            "validated": True,
        },
        "overall": {
            "orders": int(orders["order_id"].nunique()),
            "customers": overall_customers,
            "repeat_customers": repeat_customers,
            "repeat_customer_rate_pct": round(repeat_customers / overall_customers * 100, 2),
            "revenue_eur": round(overall_revenue, 2),
            "gross_profit_eur": round(overall_profit, 2),
            "average_order_value_eur": round(overall_revenue / orders["order_id"].nunique(), 2),
            "profit_margin_pct": round(overall_profit / overall_revenue * 100, 2),
        },
        "years": years,
        "monthly": summarize(orders, ["year", "month"]),
        "categories": summarize(orders, ["year", "product_category"]),
        "regions": summarize(orders, ["year", "region"]),
        "cohorts": cohort_rows,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        f"Validated {summary['metadata']['orders']} orders / "
        f"{summary['metadata']['customers']} synthetic customers. "
        f"Revenue €{summary['overall']['revenue_eur']:,.2f}; "
        f"repeat-customer rate {summary['overall']['repeat_customer_rate_pct']:.2f}%."
    )
    print(f"Dashboard data written to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
