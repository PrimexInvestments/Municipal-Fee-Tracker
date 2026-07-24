#!/usr/bin/env python3
"""
Metro Vancouver development fee scraper.

Refreshes metro_van_development_fees.xlsx from published municipal sources,
diffs every rate against what is already in the workbook, and appends anything
that moved to the Change Log tab.

    python scrape_dev_fees.py --workbook metro_van_development_fees.xlsx
    python scrape_dev_fees.py --dry-run              # fetch and diff, write nothing
    python scrape_dev_fees.py --source metro_van_dcc # one source only
    python scrape_dev_fees.py --list                 # show configured sources

Requires: requests, beautifulsoup4, lxml, openpyxl, pdfplumber
    pip install requests beautifulsoup4 lxml openpyxl pdfplumber

DESIGN NOTES
------------
Municipal fee data is published three ways, in descending order of joy:

  1. A real API.       Vancouver's open data portal. Stable, versioned, parseable.
  2. An HTML table.    Metro Vancouver. Stable enough to parse structurally.
  3. A PDF bylaw.      Most cities. Brittle. Layout changes silently break it.

This scraper handles all three but is honest about confidence. Anything it
cannot parse with confidence is written to the Change Log as NEEDS REVIEW
rather than silently guessed at or silently skipped. A fee tracker that quietly
reports stale numbers is worse than one that says "go look at this yourself."

It also cannot tell you whether a rate is legally in force. Councils give
bylaws three readings, send them to the Inspector of Municipalities, and publish
proposed rates alongside adopted ones. Always read the Status column.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    sys.exit(f"Missing dependency: {e.name}\n"
             f"Run: pip install requests beautifulsoup4 lxml pdfplumber")

UA = ("MetroVanFeeTracker/1.0 (municipal fee research; "
      "contact: you@example.com)")
TIMEOUT = 30
DELAY = 2.0  # seconds between requests to the same host

LAND_USES = [
    "Residential Lot Development Unit",
    "Townhouse Dwelling Unit",
    "Apartment Dwelling Unit",
    "Non-Residential (per square foot)",
]

# Normalises the many ways sites write the same land use
LAND_USE_ALIASES = {
    "residential lot development unit": "Residential Lot Development Unit",
    "residential lot": "Residential Lot Development Unit",
    "single family": "Residential Lot Development Unit",
    "townhouse dwelling unit": "Townhouse Dwelling Unit",
    "townhouse": "Townhouse Dwelling Unit",
    "apartment dwelling unit": "Apartment Dwelling Unit",
    "apartment": "Apartment Dwelling Unit",
    "non-residential (per square foot)": "Non-Residential (per square foot)",
    "non-residential": "Non-Residential (per square foot)",
    "non residential": "Non-Residential (per square foot)",
}


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
@dataclass
class Rate:
    """One scraped rate."""
    source_id: str
    field: str          # e.g. "Water DCC|Apartment Dwelling Unit|2026"
    value: float
    confidence: str     # high | medium | low
    note: str = ""


@dataclass
class ScrapeResult:
    source_id: str
    ok: bool
    rates: list[Rate] = field(default_factory=list)
    error: str = ""
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------
_last_hit: dict[str, float] = {}
_robots: dict[str, RobotFileParser] = {}


def robots_allow(url: str) -> bool:
    """Check robots.txt. Fail open on error -- these are public fee pages."""
    host = urlparse(url).netloc
    if host not in _robots:
        rp = RobotFileParser()
        rp.set_url(f"{urlparse(url).scheme}://{host}/robots.txt")
        try:
            rp.read()
        except Exception:
            rp = None
        _robots[host] = rp
    rp = _robots[host]
    if rp is None:
        return True
    try:
        return rp.can_fetch(UA, url)
    except Exception:
        return True


def polite_get(url: str) -> requests.Response:
    """Rate-limited GET that respects robots.txt."""
    host = urlparse(url).netloc
    if not robots_allow(url):
        raise PermissionError(f"robots.txt disallows {url}")
    since = time.time() - _last_hit.get(host, 0)
    if since < DELAY:
        time.sleep(DELAY - since)
    _last_hit[host] = time.time()
    r = requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)
    r.raise_for_status()
    return r


def money(text: str) -> float | None:
    """'$16,926' -> 16926.0 ; '$8.19' -> 8.19 ; junk -> None"""
    if text is None:
        return None
    m = re.search(r"\$?\s*([\d,]+(?:\.\d{1,2})?)", str(text).replace("\xa0", " "))
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def norm_land_use(text: str) -> str | None:
    t = re.sub(r"\s+", " ", str(text or "")).strip().lower().rstrip(":")
    t = t.replace("\u200b", "").replace("​", "")
    if t in LAND_USE_ALIASES:
        return LAND_USE_ALIASES[t]
    for alias, canon in LAND_USE_ALIASES.items():
        if t.startswith(alias):
            return canon
    return None


def cells(tr) -> list[str]:
    return [re.sub(r"\s+", " ", td.get_text(" ", strip=True)).replace("\u200b", "").strip()
            for td in tr.find_all(["td", "th"])]


# ---------------------------------------------------------------------------
# Adapter: Metro Vancouver DCC page  (HTML tables, high confidence)
# ---------------------------------------------------------------------------
def parse_metro_van_dcc(html: str, source_id: str = "metro_van_dcc") -> ScrapeResult:
    """
    The MV page renders four table groups: Water, Liquid Waste (split by
    sewerage area), Parkland Acquisition, and a Total. Columns are the
    effective dates: Jan 1 2025 / 2026 / 2027.

    We identify each table by the year header row, then walk rows. A row whose
    first cell names a sewerage area switches the active area; a row whose first
    cell is a land use yields rates.
    """
    soup = BeautifulSoup(html, "lxml")
    res = ScrapeResult(source_id=source_id, ok=True)

    tables = soup.find_all("table")
    if not tables:
        res.ok = False
        res.error = "No <table> elements found -- page structure changed."
        return res

    for tbl in tables:
        rows = tbl.find_all("tr")
        if not rows:
            continue

        # Find the year header row and map column index -> year
        year_cols: dict[int, str] = {}
        for tr in rows[:3]:
            cs = cells(tr)
            for i, c in enumerate(cs):
                ym = re.search(r"\b(20\d{2})\b", c)
                if ym and ("jan" in c.lower() or "effective" in c.lower() or ym):
                    year_cols[i] = ym.group(1)
            if year_cols:
                break
        if not year_cols:
            continue

        # Work out which component this table is, from preceding text
        context = ""
        prev = tbl.find_previous(string=re.compile(
            r"Water DCC|Liquid Waste|Parkland|Total", re.I))
        if prev:
            context = str(prev)
        low = context.lower()
        if "water" in low:
            component = "Water DCC"
        elif "liquid waste" in low:
            component = "Liquid Waste DCC"
        elif "parkland" in low:
            component = "Parkland DCC"
        elif "total" in low:
            component = "Total Regional DCC"
        else:
            component = "Unknown"
            res.warnings.append(
                f"Could not label a table (context: {context[:60]!r}); "
                f"rates recorded under 'Unknown'.")

        area = ""  # only liquid waste / total split by sewerage area
        for tr in rows:
            cs = cells(tr)
            if not cs:
                continue
            first = cs[0]

            if "sewerage area" in first.lower():
                area = re.sub(r"\s+", " ", first).strip()
                continue

            if "assist factor" in first.lower():
                for i, yr in year_cols.items():
                    if i < len(cs):
                        v = money(cs[i])
                        if v is not None:
                            res.rates.append(Rate(
                                source_id, f"{component}|Assist Factor|{yr}",
                                v, "high"))
                continue

            lu = norm_land_use(first)
            if not lu:
                continue

            for i, yr in year_cols.items():
                if i >= len(cs):
                    continue
                v = money(cs[i])
                if v is None:
                    continue
                key = f"{component}|{area + '|' if area else ''}{lu}|{yr}"
                res.rates.append(Rate(source_id, key, v, "high"))

    if not res.rates:
        res.ok = False
        res.error = "Tables found but no rates parsed -- check land use labels."
    return res


# ---------------------------------------------------------------------------
# Adapter: Opendatasoft JSON API (Vancouver open data)
# ---------------------------------------------------------------------------
def parse_opendatasoft(payload: str, source_id: str) -> ScrapeResult:
    res = ScrapeResult(source_id=source_id, ok=True)
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        res.ok = False
        res.error = f"Bad JSON: {e}"
        return res

    records = data.get("results", data.get("records", []))
    res.warnings.append(
        f"Returned {len(records)} records (dataset gives DCL district geometry, "
        f"not rates -- use it to confirm which district a parcel sits in).")
    for rec in records:
        f = rec.get("fields", rec)
        name = f.get("dcl_area") or f.get("name") or f.get("bylaw")
        if name:
            res.rates.append(Rate(source_id, f"DCL District|{name}", 0.0,
                                  "high", "district present"))
    return res


# ---------------------------------------------------------------------------
# Adapter: PDF rate table (low confidence by nature)
# ---------------------------------------------------------------------------
def parse_pdf_rates(pdf_bytes: bytes, source_id: str) -> ScrapeResult:
    res = ScrapeResult(source_id=source_id, ok=True)
    try:
        import pdfplumber
        import io
    except ImportError:
        res.ok = False
        res.error = "pdfplumber not installed"
        return res

    found = 0
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for pno, page in enumerate(pdf.pages, 1):
                for tbl in page.extract_tables() or []:
                    for row in tbl:
                        if not row or not row[0]:
                            continue
                        label = re.sub(r"\s+", " ", str(row[0])).strip()
                        vals = [money(c) for c in row[1:] if money(c) is not None]
                        if label and vals and len(label) > 3:
                            found += 1
                            res.rates.append(Rate(
                                source_id, f"p{pno}|{label}", vals[0], "low",
                                f"PDF table row; other values on row: {vals[1:]}"))
    except Exception as e:
        res.ok = False
        res.error = f"PDF parse failed: {e}"
        return res

    res.warnings.append(
        f"Extracted {found} candidate rows from PDF at LOW confidence. "
        f"PDF layout parsing is unreliable -- verify every figure by hand.")
    return res


# ---------------------------------------------------------------------------
# Adapter: generic HTML (last resort, always flags for review)
# ---------------------------------------------------------------------------
def parse_generic_html(html: str, source_id: str) -> ScrapeResult:
    """
    For sites with no stable structure. Finds dollar figures that sit near
    fee-related keywords and reports them as candidates only. This will never
    be trusted enough to auto-update a rate -- it exists to tell you 'something
    on this page looks like it changed, go look'.
    """
    res = ScrapeResult(source_id=source_id, ok=True)
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))

    kw = r"(DCC|DCL|development cost|amenity cost|per unit|per sq|per square)"
    hits = 0
    for m in re.finditer(r"\$\s?[\d,]+(?:\.\d{2})?", text):
        window = text[max(0, m.start() - 120): m.end() + 120]
        if re.search(kw, window, re.I):
            v = money(m.group())
            if v is None or v < 1:
                continue
            hits += 1
            if hits > 40:
                break
            res.rates.append(Rate(
                source_id, f"candidate@{m.start()}", v, "low",
                f"context: ...{window[:150].strip()}..."))

    res.warnings.append(
        f"Generic parser: {hits} candidate figures. NEEDS REVIEW -- no structural "
        f"parsing available for this source. Consider writing a dedicated adapter.")
    if hits == 0:
        res.warnings.append("No fee-like figures found; rates may be in a linked PDF.")
    return res


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------
PARSERS: dict[str, Callable[..., ScrapeResult]] = {
    "metro_van_dcc": lambda body, sid: parse_metro_van_dcc(body, sid),
    "vancouver_dcl": lambda body, sid: parse_generic_html(body, sid),
    "opendatasoft_api": lambda body, sid: parse_opendatasoft(body, sid),
    "pdf_rate_table": lambda body, sid: parse_pdf_rates(body, sid),
    "generic_html": lambda body, sid: parse_generic_html(body, sid),
}


def scrape_source(src: dict[str, Any]) -> ScrapeResult:
    sid, url, parser = src["id"], src["url"], src["parser"]
    try:
        r = polite_get(url)
        body = r.content if parser == "pdf_rate_table" else r.text
        return PARSERS[parser](body, sid)
    except Exception as e:
        return ScrapeResult(source_id=sid, ok=False, error=f"{type(e).__name__}: {e}")


# ---------------------------------------------------------------------------
# Data I/O  (JSON native -- the website is the source of truth)
# ---------------------------------------------------------------------------
DATA_FILE = "fee_data.json"
LOG_FILE = "change_log.json"


def load_data(path: str = DATA_FILE) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def read_sources(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"id": s["id"], "jurisdiction": s["jurisdiction"],
             "url": s["url"], "parser": s["parser"]} for s in data["sources"]]


def read_review_status(data: dict[str, Any]) -> dict[str, Any]:
    """Works out what is overdue as of today, from the same dates the site shows."""
    from datetime import date
    today = date.today()
    overdue: dict[str, list[str]] = {}
    soon: dict[str, list[str]] = {}
    for f in data["fees"]:
        nxt = f.get("nextReview")
        if not nxt:
            continue
        try:
            d = (date.fromisoformat(str(nxt)[:10]) - today).days
        except ValueError:
            continue
        bucket = overdue if d <= 0 else (soon if d <= 30 else None)
        if bucket is not None:
            bucket.setdefault(f.get("source") or "manual", []).append(
                f"{f['muni']} {f['program']}")
    return {"overdue": overdue, "soon": soon, "today": today}


def snapshot_existing(data: dict[str, Any]) -> dict[str, float]:
    """Current known values, keyed the way the parsers key their output."""
    snap: dict[str, float] = {}
    years = ("2025", "2026", "2027")
    for lu, vals in data["water"].items():
        lu = lu.replace("(per sq ft)", "(per square foot)")
        for i, y in enumerate(years):
            snap[f"Water DCC|{lu}|{y}"] = float(vals[i])
    for lu, vals in data["parkland"].items():
        lu = lu.replace("(per sq ft)", "(per square foot)")
        for i, y in enumerate(years):
            snap[f"Parkland DCC|{lu}|{y}"] = float(vals[i])
    for area, uses in data["liquidWaste"].items():
        for lu, vals in uses.items():
            lu = lu.replace("(per sq ft)", "(per square foot)")
            for i, y in enumerate(years):
                snap[f"Liquid Waste DCC|{area}|{lu}|{y}"] = float(vals[i])
    return snap


def append_changes(entries: list[dict[str, Any]], path: str = LOG_FILE) -> int:
    """Appends to the change log the website reads. Newest entries go last."""
    try:
        with open(path, encoding="utf-8") as fh:
            log = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        log = []
    log.extend(entries)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=1)
    return len(log)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=DATA_FILE, help="fee data JSON to diff against")
    ap.add_argument("--log", default=LOG_FILE, help="change log JSON to append to")
    ap.add_argument("--dry-run", action="store_true",
                    help="fetch and diff but write nothing")
    ap.add_argument("--source", action="append",
                    help="limit to these source IDs (repeatable)")
    ap.add_argument("--list", action="store_true", help="list sources and exit")
    ap.add_argument("--stale-only", action="store_true",
                    help="only scrape sources whose review date has passed")
    args = ap.parse_args()

    try:
        data = load_data(args.data)
    except FileNotFoundError:
        print(f"Data file not found: {args.data}")
        print("Run build_site.py first -- it generates fee_data.json.")
        return 1

    sources = read_sources(data)
    if args.list:
        for s in sources:
            print(f"  {s['id']:32} {s['parser']:20} {s['url']}")
        return 0

    rv = read_review_status(data)
    if rv["overdue"] or rv["soon"]:
        print(f"\nReview status as of {rv['today']}:")
        for sid, items in rv["overdue"].items():
            print(f"  OVERDUE   {sid:28} {len(items)} row(s): {items[0]}"
                  + (f" +{len(items) - 1} more" if len(items) > 1 else ""))
        for sid, items in rv["soon"].items():
            print(f"  DUE SOON  {sid:28} {len(items)} row(s): {items[0]}"
                  + (f" +{len(items) - 1} more" if len(items) > 1 else ""))
    else:
        print(f"\nReview status as of {rv['today']}: nothing overdue or due soon.")

    if args.stale_only:
        stale = set(rv["overdue"]) | set(rv["soon"])
        sources = [s for s in sources if s["id"] in stale]
        if not sources:
            print("\nNothing stale. Exiting.")
            return 0
        print(f"\n--stale-only: narrowed to {len(sources)} source(s).")

    if args.source:
        sources = [s for s in sources if s["id"] in args.source]
        if not sources:
            return print("No matching sources.") or 1

    existing = snapshot_existing(data)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entries: list[dict[str, Any]] = []
    changed = reviewed = failed = 0

    print(f"\nScraping {len(sources)} source(s)...\n")
    for src in sources:
        print(f"  {src['id']:32} ", end="", flush=True)
        res = scrape_source(src)

        if not res.ok:
            failed += 1
            print(f"FAILED  {res.error[:60]}")
            entries.append({"ts": ts, "source": src["id"], "field": "(fetch)",
                            "old": "", "new": "", "status": "FETCH FAILED",
                            "note": f"{res.error}  URL: {src['url']}"})
            continue

        hi = [r for r in res.rates if r.confidence == "high"]
        lo = [r for r in res.rates if r.confidence != "high"]
        n = 0
        for rate in hi:
            old = existing.get(rate.field)
            if old is None:
                entries.append({"ts": ts, "source": rate.source_id,
                                "field": rate.field, "old": "", "new": rate.value,
                                "status": "NEW",
                                "note": "Field not previously tracked."})
                n += 1
            elif abs(old - rate.value) > 0.005:
                entries.append({"ts": ts, "source": rate.source_id,
                                "field": rate.field, "old": old, "new": rate.value,
                                "status": "CHANGED",
                                "note": "High-confidence structural parse."})
                n += 1

        if lo:
            reviewed += 1
            entries.append({"ts": ts, "source": src["id"],
                            "field": "(low-confidence rates)", "old": "",
                            "new": len(lo), "status": "NEEDS REVIEW",
                            "note": f"{len(lo)} figures parsed at low confidence. "
                                    f"Open {src['url']} and verify by hand."})
        for w in res.warnings:
            entries.append({"ts": ts, "source": src["id"], "field": "(warning)",
                            "old": "", "new": "", "status": "INFO", "note": w})

        changed += n
        print(f"ok  {len(hi)} high-confidence, {len(lo)} low, {n} changed")

    print(f"\n  {changed} changed  |  {reviewed} need review  |  {failed} failed")

    if entries and not args.dry_run:
        total = append_changes(entries, args.log)
        print(f"  Appended {len(entries)} entries to {args.log} ({total} total)")
        print(f"  Run:  python build_site.py   to show them on the site.")
        print(f"  NOTE: rates are NOT auto-overwritten. Review the log, then edit")
        print(f"        seed_data.py deliberately and rebuild.")
    elif args.dry_run:
        print(f"  Dry run: {len(entries)} entries not written.")
    else:
        print("  No changes detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
