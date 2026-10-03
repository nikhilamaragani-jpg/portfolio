"""Generate a deterministic, fictional retail dataset for portfolio practice."""

import csv
import random
from datetime import date, timedelta
from pathlib import Path


OUTPUT = Path(__file__).resolve().parents[1] / "data" / "retail_orders.csv"
RANDOM_SEED = 20261003

PRODUCTS = {
    "Accessories": (24.0, 9.0),
    "Home": (68.0, 31.0),
    "Electronics": (185.0, 126.0),
    "Office": (52.0, 23.0),
}
REGIONS = ("North", "South", "East", "West")
CHANNELS = ("Online", "Store", "Partner")


def month_date(year: int, month: int, day: int) -> date:
    return date(year, month, min(day, 28))


def main() -> None:
    rng = random.Random(RANDOM_SEED)
    rows = []
    next_order_id = 10001

    for customer_number in range(1, 241):
        cohort_month = (customer_number - 1) % 12 + 1
        cohort_year = 2024
        acquisition = month_date(cohort_year, cohort_month, rng.randint(1, 26))
        region = REGIONS[(customer_number - 1) % len(REGIONS)]
        order_months = [cohort_month]

        repeat_count = rng.choices((0, 1, 2, 3, 4), weights=(42, 32, 18, 6, 2))[0]
        latest_month = 24
        if repeat_count and cohort_month < latest_month:
            first_gap = rng.choices((1, 2, 3, 4, 5, 6), weights=(42, 25, 16, 9, 5, 3))[0]
            next_month = cohort_month + first_gap
            if next_month <= latest_month:
                order_months.append(next_month)
                for _ in range(repeat_count - 1):
                    next_month += rng.choices((1, 2, 3, 4), weights=(40, 30, 20, 10))[0]
                    if next_month > latest_month:
                        break
                    order_months.append(next_month)

        for month_number in order_months:
            year = 2024 + (month_number - 1) // 12
            month = (month_number - 1) % 12 + 1
            order_date = acquisition if month_number == cohort_month else month_date(year, month, rng.randint(1, 26))
            category = rng.choice(tuple(PRODUCTS))
            base_price, base_cost = PRODUCTS[category]
            units = rng.randint(1, 5)
            seasonal_factor = 1.15 if month in (11, 12) else 1.0
            unit_price = round(base_price * seasonal_factor * rng.uniform(0.88, 1.12), 2)
            unit_cost = round(base_cost * rng.uniform(0.94, 1.06), 2)
            discount = rng.choice((0.0, 0.0, 0.05, 0.10, 0.15))
            channel = rng.choices(CHANNELS, weights=(55, 30, 15))[0]

            rows.append(
                {
                    "order_id": next_order_id,
                    "order_date": order_date.isoformat(),
                    "customer_id": f"C{customer_number:04d}",
                    "acquisition_date": acquisition.isoformat(),
                    "region": region,
                    "channel": channel,
                    "product_category": category,
                    "units": units,
                    "unit_price_eur": f"{unit_price:.2f}",
                    "unit_cost_eur": f"{unit_cost:.2f}",
                    "discount_rate": f"{discount:.2f}",
                }
            )
            next_order_id += 1

    rows.sort(key=lambda row: (row["order_date"], row["order_id"]))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} fictional orders for 240 fictional customers to {OUTPUT}")


if __name__ == "__main__":
    main()
