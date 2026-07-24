#!/usr/bin/env python3
"""
Regenerates index.html from the current fee data.

    python build_site.py                 # rebuild from seed_data.py
    python build_site.py --from-workbook # rebuild from the xlsx instead

Run this after scrape_dev_fees.py so the site and the spreadsheet agree.
The data is embedded directly in index.html, so the file works offline and
can be dropped on any static host with no build step or server.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
TEMPLATE = HERE / "site_template.html"
OUT = HERE / "index.html"
JSON_OUT = HERE / "fee_data.json"
LOG_IN = HERE / "change_log.json"
NEWS_IN = HERE / "news.json"


def payload_from_seed():
    import seed_data as S
    return {
        "verified": S.VERIFIED,
        "landUses": S.LAND_USES,
        "sewerageAreas": S.SEWERAGE_AREAS,
        "muniToSewerage": S.MUNI_TO_SEWERAGE,
        "water": S.MV_WATER_DCC,
        "liquidWaste": S.MV_LIQUID_WASTE_DCC,
        "parkland": S.MV_PARKLAND_DCC,
        "publishedTotal": S.MV_PUBLISHED_TOTAL,
        "vancouverDCL": S.VANCOUVER_DCL,
        "vancouverAreaDCL": S.VANCOUVER_AREA_DCL,
        "translink": S.TRANSLINK_DCC,
        "landUseToTranslink": S.LAND_USE_TO_TRANSLINK,
        "fees": [
            {"muni": m, "program": p, "landUse": l, "rate": r, "unit": u,
             "effective": e, "status": s, "bylaw": b, "source": src,
             "nextReview": n, "basis": ba, "notes": no}
            for (m, p, l, r, u, e, s, b, src, n, ba, no) in S.MUNICIPAL_FEES
        ],
        "sources": S.SOURCES,
        "upcoming": UPCOMING,
    }


def payload_from_workbook(path="metro_van_development_fees.xlsx"):
    """Reads the live workbook so scraper-applied edits flow into the site."""
    import openpyxl
    wb = openpyxl.load_workbook(path)
    base = payload_from_seed()

    fees = []
    for row in wb["Municipal Fees"].iter_rows(min_row=2, values_only=True):
        if not row[0] or str(row[0]).startswith("Pink rows"):
            continue
        nxt = row[10]
        fees.append({
            "muni": row[0], "program": row[1], "landUse": row[2],
            "rate": row[3] or 0, "unit": row[4], "effective": row[5],
            "status": row[6], "bylaw": row[7], "source": row[8],
            "nextReview": nxt.strftime("%Y-%m-%d") if hasattr(nxt, "strftime") else nxt,
            "basis": row[13], "notes": row[14],
        })
    base["fees"] = fees
    return base


UPCOMING = [
    {"date": "2026-07-24", "what": "Metro Vancouver DCC rollback bylaw adoption",
     "detail": "Board votes to roll 2026 rates back to 2025 levels and defer the 1% "
               "assist factor to 2029. No rebates for in-stream applications.",
     "impact": "high"},
    {"date": "2026-09-30", "what": "Vancouver ACC By-law takes effect",
     "detail": "New city-wide Amenity Cost Charge partly replaces negotiated CACs. "
               "Applications in stream before this date get up to 5 years protection.",
     "impact": "high"},
    {"date": "2026-09-30", "what": "Vancouver DCL annual update",
     "detail": "DCL rates adjust every Sept 30. The 20% temporary reduction is "
               "expected to be revisited in the same package.",
     "impact": "high"},
    {"date": "2027-01-01", "what": "Metro Vancouver Step 3 + TransLink adjustment",
     "detail": "Step 3 regional rates, being reduced by the July 2026 amendment. "
               "TransLink adjusts annually on Jan 1.",
     "impact": "medium"},
    {"date": "2028-01-01", "what": "Metro Vancouver new DCC program",
     "detail": "Full program update underway since 2025; new rates supersede everything.",
     "impact": "low"},
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from-workbook", action="store_true",
                    help="read fee rows from the xlsx rather than seed_data.py")
    ap.add_argument("--workbook", default="metro_van_development_fees.xlsx")
    args = ap.parse_args()

    if not TEMPLATE.exists():
        sys.exit(f"Missing template: {TEMPLATE}\n"
                 f"site_template.html must sit beside this script.")

    data = (payload_from_workbook(args.workbook) if args.from_workbook
            else payload_from_seed())

    # The change log lives in its own file so the scraper can append to it
    # without touching anything else. Embedded here so the site stays offline.
    try:
        data["changeLog"] = json.loads(LOG_IN.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        data["changeLog"] = []
        print(f"  note: no {LOG_IN.name} found; change log tab will be empty")

    try:
        data["news"] = json.loads(NEWS_IN.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        data["news"] = []
        print(f"  note: no {NEWS_IN.name} found; news tab will be empty")

    JSON_OUT.write_text(json.dumps(data, indent=1))
    html = TEMPLATE.read_text().replace("__PAYLOAD__", json.dumps(data))
    OUT.write_text(html)

    force = sum(1 for f in data["fees"] if f["status"] == "In effect")
    print(f"  {OUT.name:22} {len(html):,} bytes")
    print(f"  {JSON_OUT.name:22} {len(JSON_OUT.read_text()):,} bytes")
    print(f"  {len(data['fees'])} fee rows ({force} in force), "
          f"{len(data['sources'])} sources, {len(data['changeLog'])} log entries, "
          f"{len(data['news'])} news items")
    print(f"\n  Open index.html directly, or serve it:  python -m http.server")
    return 0


if __name__ == "__main__":
    sys.exit(main())
