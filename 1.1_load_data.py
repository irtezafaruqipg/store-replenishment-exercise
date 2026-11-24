import csv
from io import StringIO
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

def load_csv(filename):
    path = DATA_DIR / filename

    with path.open(encoding="utf-8-sig", newline="") as file:
        rows = [row for row in csv.reader(file) if row]

    if not rows:
        raise ValueError(f"{filename} is empty.")

    # In the task source files, each CSV row is wrapped in another pair of quotes.
    if len(rows[0]) == 1 and "," in rows[0][0]:
        text = "\n".join(row[0] for row in rows)
        return pd.read_csv(StringIO(text))

    return pd.read_csv(path, encoding="utf-8-sig")

OUTPUT_DIR.mkdir(exist_ok=True)

for filename in ["products.csv", "sales.csv", "Inventory.csv", "Store_notes.csv"]:
    data = load_csv(filename)
    output_file = OUTPUT_DIR / f"loaded_{filename.lower()}"
    data.to_csv(output_file, index=False)
    print(f"{filename}: {len(data)} rows saved to {output_file.name}")