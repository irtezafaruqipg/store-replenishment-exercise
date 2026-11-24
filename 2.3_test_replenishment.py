import sqlite3
from pathlib import Path

sql_file = Path(__file__).parent / "2.1_replenishment.sql"
connection = sqlite3.connect(":memory:")
connection.row_factory = sqlite3.Row

# These cases use 25 October as the reference date.
# The 100-unit rows help catch sales or stock outside the allowed dates.
connection.executescript("""
    CREATE TABLE products (
        product_id TEXT,
        product_name TEXT,
        category TEXT,
        case_pack_size INTEGER
    );

    CREATE TABLE sales (
        date TEXT,
        store_id TEXT,
        product_id TEXT,
        units_sold INTEGER
    );

    CREATE TABLE inventory (
        snapshot_date TEXT,
        store_id TEXT,
        product_id TEXT,
        units_on_hand INTEGER
    );

    INSERT INTO products VALUES
        ('P01', 'Test product', 'Test', 12),
        ('P02', 'Missing case pack', 'Test', NULL);

    INSERT INTO sales VALUES
        ('2026-10-18', 'S01', 'P01', 100),
        ('2026-10-19', 'S01', 'P01', 10),
        ('2026-10-25', 'S01', 'P01', 15),
        ('2026-10-26', 'S01', 'P01', 100),
        ('2026-10-25', 'S02', 'P01', 25),
        ('2026-10-25', 'S04', 'P02', 5),
        ('2026-10-25', 'S05', 'P01', 10);

    INSERT INTO inventory VALUES
        ('2026-10-24', 'S01', 'P01', 30),
        ('2026-10-25', 'S01', 'P01', 10),
        ('2026-10-26', 'S01', 'P01', 100),
        ('2026-10-25', 'S03', 'P01', 20),
        ('2026-10-25', 'S04', 'P02', 2),
        ('2026-10-25', 'S05', 'P01', 20);
""")

sql_query = sql_file.read_text(encoding="utf-8")
rows = connection.execute(sql_query).fetchall()
connection.close()

# Each test store has one product, so the store ID is enough for this lookup.
results = {row["store_id"]: row for row in rows}
assert len(rows) == len(results) == 5

row = results["S01"]
assert row["seven_day_sales"] == 25
assert row["average_daily_sales"] == 3.57
assert row["projected_seven_day_demand"] == 25
assert row["latest_inventory_date"] == "2026-10-25"
assert row["units_on_hand"] == 10
assert row["stock_shortfall"] == 15
assert row["recommended_order_units"] == 24
print("PASS: Uses the right sales and stock dates, then rounds up to 24 units")

row = results["S02"]
assert row["units_on_hand"] is None
assert row["stock_shortfall"] is None
assert row["recommended_order_units"] is None
print("PASS: Missing stock leaves the recommendation blank")

row = results["S03"]
assert row["seven_day_sales"] == 0
assert row["recommended_order_units"] == 0
print("PASS: Stock with no sales still appears in the report")

row = results["S04"]
assert row["stock_shortfall"] == 3
assert row["recommended_order_units"] is None
print("PASS: Missing case pack leaves the order blank and shows the shortfall")

row = results["S05"]
assert row["seven_day_sales"] == 10
assert row["units_on_hand"] == 20
assert row["stock_shortfall"] == 0
assert row["recommended_order_units"] == 0
print("PASS: Stock covers demand, so the order is zero")

print("\nAll 5 replenishment tests passed.")