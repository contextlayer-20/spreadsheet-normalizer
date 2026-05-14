#!/usr/bin/env python3
"""
Portfolio POC: normalize a deliberately messy CSV into Airtable-ready exports.

No third-party deps (stdlib only). Run from repo root:
  python scripts/normalize.py
"""

from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "messy_orders.csv"
OUT = REPO / "clean"

ALLOWED_CATEGORY = {"wholesale", "retail"}
ALLOWED_STATUS = {"pending", "shipped", "complete"}

EXCEL_ORIGIN = datetime(1899, 12, 30)


def nfkc_strip(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    return s.strip()


def parse_order_date(raw: str) -> str | None:
    raw = nfkc_strip(raw)
    if not raw:
        return None
    if raw.isdigit():
        n = int(raw)
        if 30000 <= n <= 60000:
            dt = EXCEL_ORIGIN + timedelta(days=n)
            return dt.strftime("%Y-%m-%d")
    try:
        dt = datetime.strptime(raw, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    for fmt in (
        "%m/%d/%Y",
        "%m/%d/%y",
        "%d/%m/%Y",
        "%d-%b-%y",
        "%d-%b-%Y",
        "%d-%B-%Y",
    ):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def split_amount_status(raw: str) -> tuple[float | None, str | None]:
    raw = nfkc_strip(raw)
    if not raw:
        return None, None
    m = re.match(
        r"^\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(.*)$",
        raw,
        re.IGNORECASE,
    )
    if not m:
        return None, None
    num_s, rest = m.group(1), m.group(2).strip()
    try:
        amount = float(num_s.replace(",", ""))
    except ValueError:
        amount = None
    status_hint = nfkc_strip(rest).lower() if rest else None
    return amount, status_hint


def parse_location_row(
    location: str, city: str, state: str
) -> tuple[str | None, str | None]:
    loc = nfkc_strip(location)
    c = nfkc_strip(city)
    s = nfkc_strip(state)
    if loc:
        if "," in loc:
            part1, part2 = loc.split(",", 1)
            return nfkc_strip(part1) or None, nfkc_strip(part2) or None
        m = re.match(r"^(.+?)\s+([A-Za-z]{2})$", loc)
        if m:
            return nfkc_strip(m.group(1)), m.group(2).upper()
        return loc or None, None
    if c and s:
        return c, s.upper() if len(s) == 2 else s
    return None, None


def normalize_category(raw: str) -> str | None:
    key = nfkc_strip(raw).lower()
    if key not in ALLOWED_CATEGORY:
        return None
    return key.title()


def normalize_status(raw: str, hint: str | None) -> str | None:
    base = nfkc_strip(raw).lower()
    if base in ALLOWED_STATUS:
        return base
    if hint:
        h = hint.lower()
        if "ship" in h:
            return "shipped"
        if "pend" in h:
            return "pending"
        if "complete" in h:
            return "complete"
    return None


def customer_key(name: str) -> str:
    n = nfkc_strip(name).lower()
    n = re.sub(r"[^a-z0-9]+", "-", n)
    return n.strip("-")


@dataclass
class OrderRow:
    order_id: str
    order_date: str | None
    customer_key: str
    category: str | None
    city: str | None
    state: str | None
    amount_usd: float | None
    status: str | None


def load_messy() -> list[dict[str, str]]:
    with DATA.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    raw_rows = load_messy()
    seen: set[str] = set()
    unique_raw: list[dict[str, str]] = []
    for r in raw_rows:
        oid = nfkc_strip(r.get("order_id", ""))
        if oid in seen:
            continue
        seen.add(oid)
        unique_raw.append(r)

    customers: dict[str, str] = {}
    orders: list[OrderRow] = []

    for r in unique_raw:
        cname = r.get("customer_name", "")
        ck = customer_key(cname)
        if ck and ck not in customers:
            customers[ck] = nfkc_strip(cname)

        od = parse_order_date(r.get("order_date", ""))
        city, state = parse_location_row(
            r.get("location", ""),
            r.get("city", ""),
            r.get("state", ""),
        )
        cat = normalize_category(r.get("category", ""))
        amt, hint = split_amount_status(r.get("amount_usd", ""))
        st = normalize_status(r.get("status", ""), hint)
        if st is None and hint:
            st = normalize_status("", hint)

        orders.append(
            OrderRow(
                order_id=nfkc_strip(r.get("order_id", "")),
                order_date=od,
                customer_key=ck,
                category=cat,
                city=city,
                state=state,
                amount_usd=amt,
                status=st,
            )
        )

    cust_path = OUT / "customers.csv"
    with cust_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["customer_key", "customer_name"])
        w.writeheader()
        for k in sorted(customers):
            w.writerow({"customer_key": k, "customer_name": customers[k]})

    ord_path = OUT / "orders.csv"
    with ord_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "order_id",
                "order_date",
                "customer_key",
                "category",
                "city",
                "state",
                "amount_usd",
                "status",
            ],
        )
        w.writeheader()
        for o in orders:
            w.writerow(
                {
                    "order_id": o.order_id,
                    "order_date": o.order_date or "",
                    "customer_key": o.customer_key,
                    "category": o.category or "",
                    "city": o.city or "",
                    "state": o.state or "",
                    "amount_usd": "" if o.amount_usd is None else f"{o.amount_usd:.2f}",
                    "status": o.status or "",
                }
            )

    issues: list[str] = []
    for o in orders:
        if not o.order_date:
            issues.append(f"Unparsed date for order_id {o.order_id}")
        if not o.category:
            issues.append(f"Unknown category for order_id {o.order_id}")
        if o.amount_usd is None:
            issues.append(f"Unparsed amount for order_id {o.order_id}")
        if not o.status:
            issues.append(f"Unknown status for order_id {o.order_id}")

    report = OUT / "normalization_report.txt"
    lines = [
        "Synthetic POC — normalization summary",
        "",
        f"Source rows (after dedupe on order_id): {len(orders)}",
        f"Distinct customers: {len(customers)}",
        "",
    ]
    if issues:
        lines.append("Flags (fix rules or source data):")
        lines.extend(f"  - {i}" for i in issues)
    else:
        lines.append("No blocking issues detected for this sample.")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {cust_path}")
    print(f"Wrote {ord_path}")
    print(f"Wrote {report}")


if __name__ == "__main__":
    main()
