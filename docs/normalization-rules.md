# Normalization rules (this POC)

This sample pipeline applies explicit, reviewable rules so imports stay predictable—similar to what you would document for a client before touching production data.

1. **Text hygiene:** Unicode NFKC normalization, trim leading/trailing whitespace on all string fields used in keys and labels.
2. **Order identity:** Keep the first row for each `order_id` and drop later exact duplicates (simulates a common “re-export contains dupes” issue).
3. **Dates:** Accept several human and Excel-export forms; emit a single ISO date format for Airtable.
4. **Categories & statuses:** Map only values in a defined allowlist; anything else surfaces in `normalization_report.txt` as a flag (none in the happy-path sample).
5. **Customers:** Derive a stable `customer_key` from the normalized name so Orders can reference Customers without fuzzy matching (optional next step for a production project).
6. **Location:** Prefer a single “City, ST” column when populated; otherwise fall back to separate `city` / `state`; handle a missing-comma pattern like `Boulder CO`.
7. **Amount + status collisions:** When `amount_usd` contains both a number and a word (e.g. `200 SHIPPED`), parse the number for the currency field and use the trailing token to infer status when the status column is wrong or empty.

Near-duplicate customer names (e.g. “Corner Cafe Co retail” vs “corner cafe co”) are **not** merged in this demo—on a real job you would add fuzzy matching or a manual mapping table after stakeholder review.
