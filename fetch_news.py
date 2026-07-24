#!/usr/bin/env python3
"""
Fetches development-fee news for the tracker's News tab.

    python fetch_news.py             # fetch, filter, merge into news.json
    python fetch_news.py --dry-run   # show what would be added
    python fetch_news.py --days 90   # only keep items from the last N days (default 180)

Then:  python build_site.py   to show them on the site.

HOW IT FINDS NEWS
-----------------
Two kinds of source, no API keys needed:

  1. Google News RSS. news.google.com serves an RSS feed for any search
     query. We run a handful of targeted queries (one per topic below).
  2. Municipal newsroom RSS, where a city publishes one.

Every item is filtered against fee keywords before it's kept, because a
query like "Surrey development" also returns crime stories and ribbon
cuttings. Items are deduped against what's already in news.json by URL
and by near-identical title.

WHAT GETS STORED
----------------
Headline, source, date, link, and a short snippet -- enough to decide
whether to click through. The feed points at the story; it doesn't
reproduce it. New items arrive untagged ("impact": "unreviewed") so you
can tell curated entries from raw feed arrivals on the site.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, urlparse
from xml.etree import ElementTree

try:
    import requests
except ImportError:
    sys.exit("Missing dependency. Run: pip install requests")

HERE = Path(__file__).parent
NEWS = HERE / "news.json"
UA = "MetroVanFeeTracker/1.0 (municipal fee news; contact: you@example.com)"
TIMEOUT = 30
DELAY = 1.5

# One Google News query per topic. Keep them specific; broad queries drown
# the filter in noise.
QUERIES = [
    "Metro Vancouver development cost charge",
    "Vancouver development cost levy",
    "Vancouver amenity cost charge",
    "Surrey development cost charge bylaw",
    "Burnaby development cost charge",
    "Richmond BC development cost charge",
    "New Westminster development cost charge",
    "BC amenity cost charge bylaw",
    "TransLink development cost charge",
]

# Municipal newsrooms with RSS. Not all cities have one; add as discovered.
FEEDS = [
    ("City of Surrey", "https://www.surrey.ca/rss.xml"),
    ("CivicInfo BC", "https://www.civicinfo.bc.ca/rss/news.rss"),
]

# An item must hit at least one of these to be kept.
KEEP = re.compile(
    r"development cost (charge|lev(y|ies))|DCC|DCL|amenity cost charge|ACC bylaw"
    r"|density bonus|community amenity|in-?stream protection|assist factor",
    re.I)

# ...and none of these (common false positives for "ACC"/"DCC").
DROP = re.compile(
    r"\bACC\b.*(basketball|football|tournament|conference standings)"
    r"|accident|accessib", re.I)

GNEWS = ("https://news.google.com/rss/search?q={q}"
         "&hl=en-CA&gl=CA&ceid=CA:en")


def fetch(url: str) -> str | None:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        print(f"    fetch failed: {type(e).__name__}")
        return None


def parse_rss(xml_text: str, source_hint: str = "") -> list[dict]:
    """RSS 2.0 and Atom, defensively. Returns raw candidate items."""
    out = []
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError:
        return out

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = root.iter("item")
    entries = list(items) or root.findall(".//atom:entry", ns)

    for it in entries:
        def txt(tag, atom_tag=None):
            el = it.find(tag)
            if el is None and atom_tag is not None:
                el = it.find(atom_tag, ns)
            return html.unescape((el.text or "").strip()) if el is not None and el.text else ""

        title = txt("title", "atom:title")
        link = txt("link")
        if not link:
            lel = it.find("atom:link", ns)
            link = lel.get("href", "") if lel is not None else ""
        desc = re.sub(r"<[^>]+>", " ", txt("description", "atom:summary"))
        desc = re.sub(r"\s+", " ", desc).strip()[:280]
        pub = txt("pubDate", "atom:updated")

        # Google News wraps source in the title: "Headline - Publication"
        source = source_hint
        m = re.search(r"\s[-\u2013]\s([^-\u2013]{2,40})$", title)
        if not source and m:
            source = m.group(1).strip()
            title = title[:m.start()].strip()

        date = ""
        for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z",
                    "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                date = datetime.strptime(pub.replace("GMT", "+0000"), fmt)\
                               .strftime("%Y-%m-%d")
                break
            except ValueError:
                continue

        if title and link:
            out.append({"title": title, "url": link, "summary": desc,
                        "source": source or urlparse(link).netloc,
                        "date": date})
    return out


def relevant(item: dict) -> bool:
    blob = f"{item['title']} {item['summary']}"
    return bool(KEEP.search(blob)) and not DROP.search(blob)


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()[:80]


def guess_tag(item: dict) -> str:
    blob = f"{item['title']} {item['summary']}".lower()
    for muni in ("surrey", "burnaby", "richmond", "coquitlam",
                 "new westminster", "langley", "delta", "vancouver"):
        if muni in blob:
            return muni.title()
    return "Regional"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--days", type=int, default=180,
                    help="ignore items older than this many days")
    args = ap.parse_args()

    try:
        existing = json.loads(NEWS.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []
    seen_urls = {e["url"] for e in existing}
    seen_titles = {norm_title(e["title"]) for e in existing}
    cutoff = (datetime.now(timezone.utc) - timedelta(days=args.days))\
        .strftime("%Y-%m-%d")

    candidates: list[dict] = []
    print(f"\nFetching {len(QUERIES)} news queries + {len(FEEDS)} feeds...\n")

    for q in QUERIES:
        print(f"  gnews: {q}")
        body = fetch(GNEWS.format(q=quote(q)))
        if body:
            candidates += parse_rss(body)
        time.sleep(DELAY)

    for name, url in FEEDS:
        print(f"  feed : {name}")
        body = fetch(url)
        if body:
            candidates += parse_rss(body, source_hint=name)
        time.sleep(DELAY)

    fresh, dropped_old, dropped_irrelevant = [], 0, 0
    for c in candidates:
        if c["url"] in seen_urls or norm_title(c["title"]) in seen_titles:
            continue
        if not relevant(c):
            dropped_irrelevant += 1
            continue
        if c["date"] and c["date"] < cutoff:
            dropped_old += 1
            continue
        c["tag"] = guess_tag(c)
        c["impact"] = "unreviewed"
        c["affects"] = ""
        seen_urls.add(c["url"])
        seen_titles.add(norm_title(c["title"]))
        fresh.append(c)

    print(f"\n  {len(candidates)} fetched | {len(fresh)} new & relevant | "
          f"{dropped_irrelevant} filtered | {dropped_old} too old")

    if not fresh:
        print("  Nothing new.")
        return 0

    for f in fresh[:12]:
        print(f"    + [{f.get('date') or 'undated'}] {f['title'][:76]}")
    if len(fresh) > 12:
        print(f"    ... and {len(fresh) - 12} more")

    if args.dry_run:
        print("\n  Dry run: nothing written.")
        return 0

    merged = existing + fresh
    merged.sort(key=lambda e: e.get("date") or "0000", reverse=True)
    NEWS.write_text(json.dumps(merged, indent=1))
    print(f"\n  Wrote {NEWS.name} ({len(merged)} items).")
    print(f"  Next:  python build_site.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
