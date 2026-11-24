# Store Replenishment Exercise - Technical Interview

This project validates four synthetic CSVs, recommends replenishment in SQL,
and classifies store notes using simulated model replies.

## Requirements

| Requirement | What to install |
| --- | --- |
| Python 3.12 or later | Install Python if it is missing. |
| pandas | Install from `requirements.txt`. The supported range is `pandas>=2.2.3,<4`. |
| SQLite (`sqlite3`) | Included with a standard Python installation. |
| `csv`, `io`, `json`, `pathlib`, `runpy` | Included with Python. |

pandas is the only third-party package. No credentials or API keys are needed.

## Run it locally

Open a terminal in the folder containing the project scripts. The commands
below use the Windows Python launcher. If your terminal uses `python`, replace
`py` with `python` in each command.

```powershell
py -m pip install -r requirements.txt
py 1.1_load_data.py
py 1.2_validate_data.py
py 2.2_run_replenishment.py
py 3.1_note_interpreter.py
py 2.3_test_replenishment.py
py 3.2_test_note_interpreter.py
```

The scripts read `products.csv`, `sales.csv`, `Inventory.csv`, and
`Store_notes.csv` from `data/`. The first script creates `output/`.

## Expected results

| File in `output/` | Expected result on the supplied data |
| --- | --- |
| `validation_summary.csv` | 14 findings across 16 checks. The cleaned data contains 8 products, 41 sales records, 23 stock snapshots, and 19 notes. |
| `replenishment_recommendations.csv` | 20 store and product rows, including 12 positive orders, 5 zero orders, and 3 blank recommendations. |
| `classified_store_notes.csv` | 19 notes, with 7 flagged for review. |

The last two commands should report **5 SQL checks** and **9 note-response
checks** passing. The SQL tests use the default reference date.

## What each file does

| File | Role |
| --- | --- |
| [`1.1_load_data.py`](1.1_load_data.py) | Reads the four inputs, handles the extra CSV quoting, and saves `output/loaded_*.csv`. |
| [`1.2_validate_data.py`](1.2_validate_data.py) | Checks for duplicates, missing fields, invalid dates, unknown product IDs, negative quantities, and invalid case packs. Saves `output/clean_*.csv` and the validation summary. |
| [`2.1_replenishment.sql`](2.1_replenishment.sql) | Finds the store and product pairs, totals seven-day sales, selects the latest valid stock count, and calculates recommended order quantities. |
| [`2.2_run_replenishment.py`](2.2_run_replenishment.py) | Loads the cleaned tables into SQLite, runs the SQL file, and saves the recommendations. The generated `output/replenishment.db` lets you inspect the tables used by the query. |
| [`2.3_test_replenishment.py`](2.3_test_replenishment.py) | Runs the actual SQL against a small temporary database. Covers the date window, latest stock, case rounding, missing inventory, inventory with no sales, missing case packs, and sufficient stock. |
| [`3.1_note_interpreter.py`](3.1_note_interpreter.py) | Builds the prompt, returns predefined sample replies, validates the JSON, and saves the note category and review flag. |
| [`3.2_test_note_interpreter.py`](3.2_test_note_interpreter.py) | Checks which replies the validator accepts or rejects, including a reply with an unexpected order quantity. |

## How the SQL calculates orders

1. `store_products` lists every pair found in valid sales or inventory.
2. `sales_totals` adds sales on the reference date and the six days before it.
   The daily average divides that total by seven.
3. `latest_dates` and `stock_check` find the latest eligible stock count and
   calculate the shortfall. Missing stock leaves the shortfall blank.
4. The final `SELECT` rounds the shortfall up to whole cases and reports the
   order quantity in units, with a status explaining the result.

For `STORE01 / PG001`, demand is 25 units and stock on hand is 10 units.
The 15-unit shortfall requires two cases of 12, so the recommendation is
**24 units**.

## Assumptions and limitations

- I chose **25 October 2026** as the reference date based on the supplied data.
  The default sales window is 19–25 October inclusive. To try another date,
  change the date at the top of `2.1_replenishment.sql` and rerun
  `2.2_run_replenishment.py`.
- The forecast assumes the next seven days will match the last seven. It
  excludes promotions, incoming stock, and sales missed during stockouts.
- The query uses the latest valid stock count on or before the reference date.
  A zero order means no replenishment is needed. A blank order means the
  recommendation could not be calculated because stock or case-pack
  information is missing or invalid.
- Validation removes exact duplicate rows. The cleaned sample has one stock
  count per store, product, and date. Conflicting snapshots on the same date
  would need a rule for choosing which one to use.
- The note interpreter uses predefined replies by note ID. New IDs get
  `other` and a review flag. SQL calculates orders independently of the note
  classifications.

See [dev_notes.md](dev_notes.md) for the time breakdown,
AI disclosure, and how I checked the results.