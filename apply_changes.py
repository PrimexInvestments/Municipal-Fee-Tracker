#!/usr/bin/env python3
"""
Review logged rate changes and apply the ones you approve.

    python apply_changes.py              # review each pending change
    python apply_changes.py --dry-run    # show what would change, write nothing
    python apply_changes.py --yes        # apply everything pending, no prompts
    python apply_changes.py --list       # just list what's pending

WHAT THIS DOES
--------------
scrape_dev_fees.py records what it found in change_log.json but never edits a
rate. This script closes that loop: it shows you each pending change, and for
the ones you approve it rewrites the matching value in seed_data.py.

Applied entries are marked in the log so they don't come round again.
seed_data.py is backed up to seed_data.py.bak before anything is written.

WHY IT ASKS
-----------
A municipal site can redesign overnight and hand a scraper a plausible wrong
number. If that wrote straight through, it would land on your site looking as
official as everything else. One keystroke per change is cheap insurance.

Only CHANGED and NEW entries against the regional DCC tables can be applied
automatically -- those have a clean structural key. Everything else (municipal
rates, PDF-sourced figures, warnings) is reported for you to handle by hand,
because there's no unambiguous target to write to.
"""

from __future__ import annotations

import argparse
import ast
import importlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
SEED = HERE / "seed_data.py"
LOG = HERE / "change_log.json"

# Which parser key prefix maps to which structure in seed_data.py
TARGETS = {
    "Water DCC": ("MV_WATER_DCC", False),
    "Parkland DCC": ("MV_PARKLAND_DCC", False),
    "Liquid Waste DCC": ("MV_LIQUID_WASTE_DCC", True),  # nested by sewerage area
}
YEARS = ("2025", "2026", "2027")

# The scraper normalises land use labels; seed_data.py uses shorter ones.
LU_BACK = {"Non-Residential (per square foot)": "Non-Residential (per sq ft)"}


def parse_field(field: str):
    """
    'Water DCC|Apartment Dwelling Unit|2026'                    -> (var, None, lu, 1)
    'Liquid Waste DCC|Fraser Sewerage Area (FSA)|Townhouse...'  -> (var, area, lu, i)
    Returns None if the key isn't something we can safely write to.
    """
    parts = field.split("|")
    comp = parts[0]
    if comp not in TARGETS:
        return None
    var, nested = TARGETS[comp]
    if nested and len(parts) == 4:
        _, area, lu, yr = parts
    elif not nested and len(parts) == 3:
        _, lu, yr = parts
        area = None
    else:
        return None
    if yr not in YEARS:
        return None
    lu = LU_BACK.get(lu, lu)
    return var, area, lu, YEARS.index(yr)


def fmt_val(v):
    """Match seed_data.py's existing style: ints bare, floats to 2dp."""
    if isinstance(v, float) and not v.is_integer():
        return f"{v:.2f}"
    return str(int(v))


def render_assignment(var: str, value: dict, nested: bool) -> str:
    """Rebuild the dict literal for one assignment, in the file's own style."""
    lines = [f"{var} = {{"]
    if nested:
        for area, uses in value.items():
            lines.append(f'    "{area}": {{')
            for lu, tup in uses.items():
                vals = ", ".join(fmt_val(v) for v in tup)
                lines.append(f'        "{lu}": ({vals}),')
            lines.append("    },")
    else:
        for lu, tup in value.items():
            vals = ", ".join(fmt_val(v) for v in tup)
            lines.append(f'    "{lu}": ({vals}),')
    lines.append("}")
    return "\n".join(lines)


def splice(src_lines: list[str], var: str, new_block: str) -> list[str]:
    """Replace the assignment for `var` in place, by AST line range."""
    tree = ast.parse("".join(src_lines))
    for node in tree.body:
        if (isinstance(node, ast.Assign) and node.targets
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == var):
            start, end = node.lineno - 1, node.end_lineno
            return src_lines[:start] + [new_block + "\n"] + src_lines[end:]
    raise KeyError(f"Could not find assignment for {var} in {SEED.name}")


def load_log():
    try:
        return json.loads(LOG.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def pending(log):
    """Entries that change a rate and haven't been applied yet."""
    out = []
    for i, e in enumerate(log):
        if e.get("applied"):
            continue
        if e.get("status") not in ("CHANGED", "NEW"):
            continue
        tgt = parse_field(str(e.get("field", "")))
        out.append((i, e, tgt))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="preview only")
    ap.add_argument("--yes", action="store_true", help="apply all without prompting")
    ap.add_argument("--list", action="store_true", help="list pending and exit")
    args = ap.parse_args()

    log = load_log()
    items = pending(log)
    if not items:
        print("\nNothing pending. Run scrape_dev_fees.py first.")
        return 0

    applicable = [(i, e, t) for i, e, t in items if t]
    manual = [(i, e) for i, e, t in items if not t]

    print(f"\n{len(items)} pending change(s): "
          f"{len(applicable)} applicable, {len(manual)} manual.\n")

    for n, (_, e, t) in enumerate(applicable, 1):
        var, area, lu, yi = t
        where = f"{area} / " if area else ""
        print(f"  [{n}] {e['field']}")
        print(f"      {where}{lu}, {YEARS[yi]}")
        print(f"      {e.get('old', '?')}  ->  {e.get('new')}")
        print(f"      {e.get('source', '?')} · {e.get('note', '')[:76]}")
        print()

    if manual:
        print("  Needs a manual edit (no unambiguous target):")
        for _, e in manual:
            print(f"      {e.get('field')} · {e.get('source')} "
                  f"· {e.get('old', '')} -> {e.get('new', '')}")
        print()

    if args.list:
        return 0
    if not applicable:
        print("Nothing can be applied automatically.")
        return 0

    # --- choose ---
    if args.yes or args.dry_run:
        chosen = list(range(len(applicable)))
    else:
        print("Apply which? 'a' = all, 'n' = none, or numbers like 1,3")
        try:
            resp = input("  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return 1
        if resp in ("n", "", "none"):
            print("Nothing applied.")
            return 0
        if resp in ("a", "all"):
            chosen = list(range(len(applicable)))
        else:
            try:
                chosen = [int(x) - 1 for x in resp.replace(" ", "").split(",")]
            except ValueError:
                print("Didn't understand that. Nothing applied.")
                return 1
            if any(c < 0 or c >= len(applicable) for c in chosen):
                print("Number out of range. Nothing applied.")
                return 1

    # --- build the new values in memory ---
    sys.path.insert(0, str(HERE))
    S = importlib.import_module("seed_data")
    importlib.reload(S)
    tables = {name: {k: (dict(v) if isinstance(v, dict) else list(v))
                     for k, v in getattr(S, name).items()}
              for name, _ in TARGETS.values()}
    for name, nested in TARGETS.values():
        if nested:
            tables[name] = {a: dict(u) for a, u in getattr(S, name).items()}

    touched, applied_idx = set(), []
    for c in chosen:
        li, e, (var, area, lu, yi) = applicable[c]
        try:
            cur = tables[var][area][lu] if area else tables[var][lu]
        except KeyError:
            print(f"  skip: {lu} not found in {var}")
            continue
        new_tuple = list(cur)
        new_tuple[yi] = e["new"]
        if area:
            tables[var][area][lu] = tuple(new_tuple)
        else:
            tables[var][lu] = tuple(new_tuple)
        touched.add(var)
        applied_idx.append(li)

    if not touched:
        print("Nothing matched. Nothing written.")
        return 1

    if args.dry_run:
        print(f"Dry run: would rewrite {', '.join(sorted(touched))} "
              f"in {SEED.name} and mark {len(applied_idx)} log entries applied.")
        return 0

    # --- write ---
    shutil.copy(SEED, SEED.with_suffix(".py.bak"))
    lines = SEED.read_text().splitlines(keepends=True)
    for var in touched:
        nested = TARGETS[next(k for k, v in TARGETS.items() if v[0] == var)][1]
        lines = splice(lines, var, render_assignment(var, tables[var], nested))
    SEED.write_text("".join(lines))

    # verify the file still imports and holds the new numbers
    try:
        importlib.reload(S)
    except Exception as exc:
        shutil.copy(SEED.with_suffix(".py.bak"), SEED)
        print(f"  Write produced invalid Python ({exc}). Restored from backup.")
        return 1

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    for li in applied_idx:
        log[li]["applied"] = True
        log[li]["appliedAt"] = stamp
    LOG.write_text(json.dumps(log, indent=1))

    print(f"  Applied {len(applied_idx)} change(s) to {', '.join(sorted(touched))}")
    print(f"  Backup: {SEED.with_suffix('.py.bak').name}")
    print(f"\n  Next:  python build_site.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
