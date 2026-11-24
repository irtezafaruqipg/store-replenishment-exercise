from pathlib import Path

import pandas as pd

OUTPUT_DIR = Path(__file__).parent / "output"

products = pd.read_csv(OUTPUT_DIR / "loaded_products.csv")
sales = pd.read_csv(OUTPUT_DIR / "loaded_sales.csv")
inventory = pd.read_csv(OUTPUT_DIR / "loaded_inventory.csv")
store_notes = pd.read_csv(OUTPUT_DIR / "loaded_store_notes.csv")

# To check rows removed, saving initial row count for each table
initial_products = len(products)
initial_sales = len(sales)
initial_inventory = len(inventory)
initial_notes = len(store_notes)

duplicate_products = products.duplicated().sum()
duplicate_sales = sales.duplicated().sum()
duplicate_inventory = inventory.duplicated().sum()
duplicate_notes = store_notes.duplicated().sum()

products = products.drop_duplicates()
sales = sales.drop_duplicates()
inventory = inventory.drop_duplicates()
store_notes = store_notes.drop_duplicates()

# Product table is checked for missing required values and invalid case pack sizes
missing_products = products[["product_id", "product_name", "category"]].isna().any(axis=1)
bad_case_pack = products["case_pack_size"].isna() | (products["case_pack_size"] <= 0)

# We will keep the product visible even if we cannot calculate a whole-case order as we will give a recommendation for it later
clean_products = products[~missing_products].copy()
clean_products.loc[bad_case_pack, "case_pack_size"] = float("nan")
known_products = clean_products["product_id"]

# Sales checks
sales_fields = ["sales_record_id", "date", "store_id", "product_id", "units_sold"]
missing_sales = sales[sales_fields].isna().any(axis=1)

sales_dates = pd.to_datetime(sales["date"], format="%Y-%m-%d", errors="coerce")
invalid_sales_dates = sales["date"].notna() & sales_dates.isna()
unknown_sales = sales["product_id"].notna() & ~sales["product_id"].isin(known_products)
negative_sales = sales["units_sold"] < 0

bad_sales = missing_sales | invalid_sales_dates | unknown_sales | negative_sales
clean_sales = sales[~bad_sales]

# Inventory checks
inventory_fields = ["snapshot_date", "store_id", "product_id", "units_on_hand"]
missing_inventory = inventory[inventory_fields].isna().any(axis=1)

stock_dates = pd.to_datetime(inventory["snapshot_date"], format="%Y-%m-%d", errors="coerce")
invalid_inventory_dates = inventory["snapshot_date"].notna() & stock_dates.isna()
unknown_inventory = inventory["product_id"].notna() & ~inventory["product_id"].isin(known_products)
negative_inventory = inventory["units_on_hand"] < 0

bad_inventory = missing_inventory | invalid_inventory_dates | unknown_inventory | negative_inventory
clean_inventory = inventory[~bad_inventory]

# Store note checks
note_fields = ["note_id", "store_id", "product_id", "note_text"]
missing_notes = store_notes[note_fields].isna().any(axis=1)
unknown_notes = store_notes["product_id"].notna() & ~store_notes["product_id"].isin(known_products)
clean_store_notes = store_notes[~(missing_notes | unknown_notes)]

# Counting the flagged rows for each check and saving to Validation Summary for data quality check
summary = pd.DataFrame(
    [
        ("Products.csv", "Duplicate record", duplicate_products, "Duplicate removed"),
        ("Sales.csv", "Duplicate record", duplicate_sales, "Duplicate removed"),
        ("Inventory.csv", "Duplicate record", duplicate_inventory, "Duplicate removed"),
        ("Store_notes.csv", "Duplicate record", duplicate_notes, "Duplicate removed"),
        ("Sales.csv", "Invalid date", invalid_sales_dates.sum(), "Row removed"),
        ("Inventory.csv", "Invalid date", invalid_inventory_dates.sum(), "Row removed"),
        ("Products.csv", "Missing required value", missing_products.sum(), "Row removed"),
        ("Sales.csv", "Missing required value", missing_sales.sum(), "Row removed"),
        ("Inventory.csv", "Missing required value", missing_inventory.sum(), "Row removed"),
        ("Store_notes.csv", "Missing required value", missing_notes.sum(), "Row removed"),
        ("Sales.csv", "Unknown product", unknown_sales.sum(), "Row removed"),
        ("Inventory.csv", "Unknown product", unknown_inventory.sum(), "Row removed"),
        ("Store_notes.csv", "Unknown product", unknown_notes.sum(), "Row removed"),
        ("Sales.csv", "Negative quantity", negative_sales.sum(), "Row removed"),
        ("Inventory.csv", "Negative quantity", negative_inventory.sum(), "Row removed"),
        ("Products.csv", "Invalid case pack", bad_case_pack.sum(),
         "Product retained with blank case-pack size"),
    ],
    columns=["Source File", "Issue", "Count", "Action"],
)

clean_products.to_csv(OUTPUT_DIR / "clean_products.csv", index=False)
clean_sales.to_csv(OUTPUT_DIR / "clean_sales.csv", index=False)
clean_inventory.to_csv(OUTPUT_DIR / "clean_inventory.csv", index=False)
clean_store_notes.to_csv(OUTPUT_DIR / "clean_store_notes.csv", index=False)
summary.to_csv(OUTPUT_DIR / "validation_summary.csv", index=False)

print(summary.to_string(index=False))
print(f"\nTotal findings: {summary['Count'].sum()}")
print(f"Products: {initial_products} -> {len(clean_products)}")
print(f"Sales: {initial_sales} -> {len(clean_sales)}")
print(f"Inventory: {initial_inventory} -> {len(clean_inventory)}")
print(f"Store notes: {initial_notes} -> {len(clean_store_notes)}")