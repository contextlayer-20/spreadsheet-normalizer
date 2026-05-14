# Field map (messy spreadsheet → Airtable)

Synthetic POC only. Intended to show how source columns align to a normalized schema before import.

| Source (`data/messy_orders.csv`) | Airtable / clean export | Notes |
|----------------------------------|-------------------------|-------|
| `order_id` | **Orders**: `order_id` (primary field — text) | Deduplicated on first occurrence in this POC. |
| `order_date` | **Orders**: `order_date` (date) | Normalized to ISO `YYYY-MM-DD` from slash dates, short month tokens, `%d-%b-%y`, `%d-%m-%Y`, and Excel serials. |
| `customer_name` | **Customers**: `customer_name` (text) + **`customer_key`** (text helper) | `customer_key` is a deterministic slug (`acme-wholesale`). **Orders** link via `customer_key` → Customers record (use Airtable *Link to another record* after customer import). |
| `category` | **Orders**: `category` (single select) | Allowed values in script: Wholesale, Retail (`ALLOWED_CATEGORY`). |
| `location` / `city` / `state` | **Orders**: `city` (text), `state` (text) | Prefer `city, ST` from `location` when present; otherwise use `city` + `state`. `"Boulder CO"` without comma is split heuristically. |
| `amount_usd` | **Orders**: `amount_usd` (currency/number) | Strips `$`/`$` and commas; supports `"200 SHIPPED"` style merged status + amount. |
| `status` | **Orders**: `status` (single select) | Allowed values: pending, shipped, complete. Mixed casing normalized; inferred from trailing word in amount when needed. |

**Import order:** 1) `clean/customers.csv` into **Customers** (match on `customer_key`). 2) `clean/orders.csv` into **Orders**, mapping `customer_key` to the link field by matching the primary or a unique key on Customers.
