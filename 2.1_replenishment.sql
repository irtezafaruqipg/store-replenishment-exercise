-- I used 25 October as the reference date based on the sample data as stated in problem statement
-- The reference date is used to calculate the last seven days of sales and to determine the latest inventory snapshot before this date.
WITH settings AS (
    SELECT '2026-10-25' AS reference_date
),

-- A store can have a stock count without any sales, or sales without a stock count.
store_products AS (
    SELECT store_id, product_id FROM sales
    UNION
    SELECT store_id, product_id FROM inventory
),

-- Included the reference date and the six days before it.
sales_totals AS (
    SELECT store_id, product_id, SUM(units_sold) AS seven_day_sales
    FROM sales
    CROSS JOIN settings
    WHERE date BETWEEN DATE(reference_date, '-6 days') AND reference_date
    GROUP BY store_id, product_id
),

-- Ignore stock counts taken after the reference date.
latest_dates AS (
    SELECT store_id, product_id, MAX(snapshot_date) AS latest_inventory_date
    FROM inventory
    CROSS JOIN settings
    WHERE snapshot_date <= reference_date
    GROUP BY store_id, product_id
),

-- Use the stock count from that latest date.
stock_check AS (
    SELECT
        pairs.store_id,
        pairs.product_id,
        products.product_name,
        products.category,
        settings.reference_date,
        COALESCE(sales_totals.seven_day_sales, 0) AS seven_day_sales,
        latest_dates.latest_inventory_date,
        inventory.units_on_hand,
        products.case_pack_size,

        -- If we have no stock count, we leave the shortfall blank.
        -- If stock covers demand, the shortfall is zero.
        MAX(COALESCE(sales_totals.seven_day_sales, 0) - inventory.units_on_hand, 0)
            AS stock_shortfall
    FROM store_products AS pairs
    CROSS JOIN settings
    JOIN products ON products.product_id = pairs.product_id
    LEFT JOIN sales_totals USING (store_id, product_id)
    LEFT JOIN latest_dates USING (store_id, product_id)
    LEFT JOIN inventory
        ON inventory.store_id = pairs.store_id
        AND inventory.product_id = pairs.product_id
        AND inventory.snapshot_date = latest_dates.latest_inventory_date
)

SELECT
    store_id,
    product_id,
    product_name,
    category,
    reference_date,
    seven_day_sales,
    ROUND(seven_day_sales / 7.0, 2) AS average_daily_sales,

    -- We assume the next seven days will match the last seven.
    seven_day_sales AS projected_seven_day_demand,

    latest_inventory_date,
    units_on_hand,
    stock_shortfall,
    case_pack_size,

    -- Round up to whole cases. A gap of 15 with a pack of 12 needs 24 units.
    CASE
        WHEN units_on_hand IS NOT NULL
             AND case_pack_size > 0
             AND case_pack_size = CAST(case_pack_size AS INTEGER)
        THEN CAST((stock_shortfall + case_pack_size - 1) / case_pack_size AS INTEGER)
             * CAST(case_pack_size AS INTEGER)
    END AS recommended_order_units,

    -- Explain whether a blank order needs a stock check or a case-pack check.
    CASE
        WHEN units_on_hand IS NULL THEN 'No recommendation: missing inventory'
        WHEN case_pack_size IS NULL OR case_pack_size <= 0
             OR case_pack_size != CAST(case_pack_size AS INTEGER)
            THEN 'No recommendation: invalid case-pack size'
        WHEN stock_shortfall = 0 THEN 'No order required'
        ELSE 'Replenishment recommended'
    END AS recommendation_status
FROM stock_check
ORDER BY store_id, product_id;