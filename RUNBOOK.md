# Runbook — Spreadsheet normalizer (portfolio POC)

Step-by-step instructions to run this repo locally or in CI. Everything uses **Python 3.10+** and the **standard library only**—no virtual environment or packages are required.

## 1. Purpose

Reads `data/messy_orders.csv`, applies normalization rules, and writes:

- `clean/customers.csv`
- `clean/orders.csv`
- `clean/normalization_report.txt`

Paths are resolved **relative to the repository root**, not the script directory.

## 2. Prerequisites

| Requirement | Notes |
|-------------|--------|
| Python | 3.10 or newer (`python --version` or `python3 --version`) |
| Repository | Full checkout with `data/messy_orders.csv` present |

## 3. Clone and enter the repo

```bash
git clone https://github.com/contextlayer-20/spreadsheet-normalizer.git
cd spreadsheet-normalizer
```

If your local folder name differs (for example after a fork), `cd` into that folder instead.

## 4. Run the normalizer

From the **repository root** (same directory as `README.md`):

```bash
python scripts/normalize.py
```

Example with Python 3 explicitly:

```bash
python3 scripts/normalize.py
```

### Expected stdout

Three lines naming the paths written:

- `.../clean/customers.csv`
- `.../clean/orders.csv`
- `.../clean/normalization_report.txt`

### If the command fails

- **Wrong working directory:** Symptoms include `No such file` for `messy_orders.csv`. Fix: `cd` to repo root until `ls data/messy_orders.csv` succeeds.
- **Python too old:** If you see syntax errors on union types (`str | None`), upgrade to Python 3.10+.

## 5. Confirm success

1. Read `clean/normalization_report.txt`.  
   For the stock sample data you should see **no blocking flags** (“No blocking issues detected for this sample.”).
2. Spot-check CSVs exist and have headers:
   ```bash
   head -n 3 clean/orders.csv clean/customers.csv
   ```
3. Optional: repeat the QA list in [`docs/verification-checklist.md`](docs/verification-checklist.md).

## 6. After changing the source data

If you edit `data/messy_orders.csv` or change rules in `scripts/normalize.py`:

1. Run `python scripts/normalize.py` again from the repo root.
2. Review `clean/normalization_report.txt` for new flags.
3. Commit updated `clean/*.csv` and `normalization_report.txt` if you want the repo to stay in sync for reviewers.

## 7. Optional: treat `clean/` as build artifacts

For a “generate on demand” workflow you can add `clean/` to `.gitignore` and run the script before imports. This repo **commits** `clean/` so people can read outputs without running Python; that is a product choice, not a technical requirement.

## 8. Related docs

| Doc | Use when |
|-----|----------|
| [`docs/field-map.md`](docs/field-map.md) | Mapping columns to Airtable-style fields |
| [`docs/normalization-rules.md`](docs/normalization-rules.md) | What the script is doing in plain language |
| [`docs/verification-checklist.md`](docs/verification-checklist.md) | Pre/post migration checks |

## 9. Optional: re-export the README demo GIF

Source recording: `assets/Screencast from 2026-05-14 11-33-14.webm` (replace with your own file as needed). Requires **ffmpeg**.

From the repository root:

```bash
bash scripts/export-demo-gif.sh \
  "assets/Screencast from 2026-05-14 11-33-14.webm" \
  "assets/spreadsheet-normalizer-demo.gif"
```

To shrink long captures, trim with `DEMO_GIF_START` and `DEMO_GIF_DURATION` (seconds). See comments in `scripts/export-demo-gif.sh`.
