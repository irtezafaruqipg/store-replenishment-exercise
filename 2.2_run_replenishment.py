import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"

products = pd.read_csv(OUTPUT_DIR / "clean_products.csv")
sales = pd.read_csv(OUTPUT_DIR / "clean_sales.csv")
inventory = pd.read_csv(OUTPUT_DIR / "clean_inventory.csv")

# Saving the database so I can inspect the tables if a result looks wrong
connection = sqlite3.connect(OUTPUT_DIR / "replenishment.db")
products.to_sql("products", connection, if_exists="replace", index=False)
sales.to_sql("sales", connection, if_exists="replace", index=False)
inventory.to_sql("inventory", connection, if_exists="replace", index=False)

sql_file = BASE_DIR / "2.1_replenishment.sql"
sql_query = sql_file.read_text(encoding="utf-8")
recommendations = pd.read_sql_query(sql_query, connection)
connection.close()

output_file = OUTPUT_DIR / "replenishment_recommendations.csv"
recommendations.to_csv(output_file, index=False)

print(recommendations.head().to_string(index=False))
print(f"\nSaved {len(recommendations)} store-product rows to {output_file.name}")