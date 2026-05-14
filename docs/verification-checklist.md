# Verification checklist (before / after import)

Use this as a template for a real migration. For this repo, run `python scripts/normalize.py` and confirm each item.

## Source vs output

- [ ] **Row count:** After dedupe on `order_id`, `clean/orders.csv` row count matches expectation (here: 8 data rows + header).
- [ ] **Primary key:** No duplicate `order_id` in `clean/orders.csv`.
- [ ] **Customers:** `clean/customers.csv` has one row per distinct `customer_key`; count matches script report (here: 6).

## Data quality

- [ ] **Dates:** All `order_date` values are ISO `YYYY-MM-DD` and fall in a plausible range.
- [ ] **Categories:** Every `category` is in the allowlist (Wholesale / Retail for this POC).
- [ ] **Statuses:** Every `status` is in the allowlist (pending / shipped / complete).
- [ ] **Amounts:** `amount_usd` parses as a number for every order; spot-check a few against the raw file.
- [ ] **Geography:** For rows with `location` or `city`/`state`, `city` and `state` are filled when the source had enough information (note: row `1006` deliberately has no location in the sample).

## Airtable (if you import the clean CSVs)

- [ ] **Link integrity:** Every `customer_key` on Orders exists on Customers.
- [ ] **Single select options:** Airtable options match normalized values (or use pre-created options before import).
- [ ] **Spot samples:** Manually compare 3–5 random orders to the original messy sheet.

## Automation

- [ ] Read `clean/normalization_report.txt` after each run; resolve any listed flags before importing.
