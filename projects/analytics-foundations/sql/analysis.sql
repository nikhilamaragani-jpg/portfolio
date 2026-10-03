-- Foundational analyst questions for the synthetic retail_orders table.
-- SQL dialect: SQLite. Import data/retail_orders.csv with headers first.
-- Revenue is recognized after line-level discount; gross profit is revenue less unit cost.

-- 1. Data quality checks
SELECT
    COUNT(*) AS order_rows,
    COUNT(DISTINCT order_id) AS unique_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(CASE WHEN order_date < acquisition_date THEN 1 ELSE 0 END) AS invalid_order_dates
FROM retail_orders;

-- 2. Monthly sales and profitability
SELECT
    strftime('%Y-%m', order_date) AS order_month,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(units * unit_price_eur * (1 - discount_rate)), 2) AS revenue_eur,
    ROUND(SUM(units * (unit_price_eur * (1 - discount_rate) - unit_cost_eur)), 2) AS gross_profit_eur,
    ROUND(
        100.0 * SUM(units * (unit_price_eur * (1 - discount_rate) - unit_cost_eur))
        / NULLIF(SUM(units * unit_price_eur * (1 - discount_rate)), 0),
        2
    ) AS profit_margin_pct
FROM retail_orders
GROUP BY strftime('%Y-%m', order_date)
ORDER BY order_month;

-- 3. Category performance
SELECT
    product_category,
    COUNT(DISTINCT order_id) AS orders,
    SUM(units) AS units_sold,
    ROUND(SUM(units * unit_price_eur * (1 - discount_rate)), 2) AS revenue_eur,
    ROUND(SUM(units * (unit_price_eur * (1 - discount_rate) - unit_cost_eur)), 2) AS gross_profit_eur
FROM retail_orders
GROUP BY product_category
ORDER BY revenue_eur DESC;

-- 4. Repeat purchase rate. Denominator: distinct customers with at least one order.
WITH customer_order_counts AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
    FROM retail_orders
    GROUP BY customer_id
)
SELECT
    COUNT(*) AS customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(
        100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
        2
    ) AS repeat_customer_rate_pct
FROM customer_order_counts;

-- 5. Cohort retention. Month 0 is the acquisition month; later values are
-- customers placing at least one order in that specific elapsed calendar month.
WITH activity AS (
    SELECT DISTINCT
        customer_id,
        strftime('%Y-%m', acquisition_date) AS cohort_month,
        strftime('%Y-%m', order_date) AS activity_month,
        (
            (CAST(strftime('%Y', order_date) AS INTEGER) - CAST(strftime('%Y', acquisition_date) AS INTEGER)) * 12
            + CAST(strftime('%m', order_date) AS INTEGER) - CAST(strftime('%m', acquisition_date) AS INTEGER)
        ) AS months_since_acquisition
    FROM retail_orders
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_customers
    FROM activity
    GROUP BY cohort_month
)
SELECT
    a.cohort_month,
    a.months_since_acquisition,
    c.cohort_customers,
    COUNT(DISTINCT a.customer_id) AS retained_customers,
    ROUND(100.0 * COUNT(DISTINCT a.customer_id) / c.cohort_customers, 1) AS retention_pct
FROM activity AS a
JOIN cohort_sizes AS c USING (cohort_month)
GROUP BY a.cohort_month, a.months_since_acquisition, c.cohort_customers
ORDER BY a.cohort_month, a.months_since_acquisition;
