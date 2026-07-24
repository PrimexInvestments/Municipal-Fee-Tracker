"""Tests the Metro Vancouver parser against a fixture mirroring the live page."""

from scrape_dev_fees import parse_metro_van_dcc, parse_generic_html

# Mirrors the real structure: an <h3>-ish label, then a table whose header row
# carries the effective dates, an assist factor row, then land-use rows.
# Liquid waste splits by sewerage area using a full-width label row.
FIXTURE = """
<html><body>
<h3>Water DCC</h3>
<table>
<tr><th>Effective Date</th><th>Jan 1, 2025</th><th>Jan 1, 2026</th><th>Jan 1, 2027</th></tr>
<tr><td>Assist Factor</td><td>45%</td><td>15%</td><td>1%</td></tr>
<tr><td>Residential Lot Development Unit</td><td>$10,952</td><td>$16,926</td><td>$19,714</td></tr>
<tr><td>Townhouse Dwelling Unit</td><td>$9,839</td><td>$15,206</td><td>$17,710</td></tr>
<tr><td>Apartment Dwelling Unit</td><td>$6,791</td><td>$10,495</td><td>$12,223</td></tr>
<tr><td>Non-Residential (per square foot)</td><td>$5.30</td><td>$8.19</td><td>$9.54&#8203;</td></tr>
</table>

<h3>Liquid Waste DCC</h3>
<table>
<tr><th>Effective Date</th><th>Jan 1, 2025</th><th>Jan 1, 2026</th><th>Jan 1, 2027</th></tr>
<tr><td>Assist Factor</td><td>16%</td><td>10%</td><td>1%</td></tr>
<tr><td colspan="4"><strong>Vancouver Sewerage Area (VSA)</strong></td></tr>
<tr><td>Residential Lot Development Unit</td><td>$10,498</td><td>$11,290</td><td>$12,476</td></tr>
<tr><td>Townhouse Dwelling Unit</td><td>$9,593</td><td>$10,316</td><td>$11,400</td></tr>
<tr><td>Apartment Dwelling Unit</td><td>$6,298</td><td>$6,772</td><td>$7,484</td></tr>
<tr><td>Non-Residential (per square foot)</td><td>$5.30</td><td>$5.70</td><td>$6.30</td></tr>
<tr><td colspan="4"><strong>Fraser Sewerage Area (FSA)</strong></td></tr>
<tr><td>Residential Lot Development Unit</td><td>$11,443</td><td>$12,311</td><td>$13,613</td></tr>
<tr><td>Townhouse Dwelling Unit</td><td>$10,015</td><td>$10,775</td><td>$11,914</td></tr>
<tr><td>Apartment Dwelling Unit</td><td>$7,302</td><td>$7,855</td><td>$8,686</td></tr>
<tr><td>Non-Residential (per square foot)</td><td>$5.41</td><td>$5.82</td><td>$6.43</td></tr>
</table>

<h3>Parkland Acquisition DCC</h3>
<table>
<tr><th>Effective Date</th><th>Jan 1, 2025</th><th>Jan 1, 2026</th><th>Jan 1, 2027</th></tr>
<tr><td>Assist Factor</td><td>75%</td><td>50%</td><td>1%</td></tr>
<tr><td>Residential Lot Development Unit</td><td>$491</td><td>$981</td><td>$1,943&#8203;</td></tr>
<tr><td>Townhouse Dwelling Unit</td><td>$442</td><td>$884</td><td>$1,751</td></tr>
<tr><td>Apartment Dwelling Unit</td><td>$303</td><td>$606</td><td>$1,199</td></tr>
<tr><td>Non-Residential (per square foot)</td><td>$0.24</td><td>$0.48</td><td>$0.94</td></tr>
</table>
</body></html>
"""

EXPECT = {
    "Water DCC|Residential Lot Development Unit|2026": 16926,
    "Water DCC|Apartment Dwelling Unit|2027": 12223,
    "Water DCC|Non-Residential (per square foot)|2027": 9.54,
    "Liquid Waste DCC|Vancouver Sewerage Area (VSA)|Apartment Dwelling Unit|2026": 6772,
    "Liquid Waste DCC|Fraser Sewerage Area (FSA)|Residential Lot Development Unit|2025": 11443,
    "Liquid Waste DCC|Fraser Sewerage Area (FSA)|Non-Residential (per square foot)|2027": 6.43,
    "Parkland DCC|Apartment Dwelling Unit|2026": 606,
    "Parkland DCC|Residential Lot Development Unit|2027": 1943,
}

res = parse_metro_van_dcc(FIXTURE)
got = {r.field: r.value for r in res.rates}

print(f"parsed ok={res.ok}  rates={len(res.rates)}  warnings={len(res.warnings)}")
for w in res.warnings:
    print("  WARN:", w)
print()

fails = 0
for k, want in EXPECT.items():
    have = got.get(k)
    ok = have is not None and abs(have - want) < 0.005
    if not ok:
        fails += 1
    print(f"  {'OK  ' if ok else 'FAIL'} {k:78} want={want} got={have}")

# Sewerage-area attribution must not leak across sections.
# Assist factors apply to the whole component, so they carry no area -- exclude them.
leak = [k for k in got if k.startswith("Liquid Waste")
        and "Sewerage Area" not in k and "Assist Factor" not in k]
print(f"\n  {'OK  ' if not leak else 'FAIL'} liquid-waste rows all carry a sewerage area "
      f"({len(leak)} unattributed)")
fails += bool(leak)

# Assist factors captured
af = [k for k in got if "Assist Factor" in k]
print(f"  {'OK  ' if len(af) == 9 else 'FAIL'} assist factors captured: {len(af)} (expect 9)")
fails += (len(af) != 9)

# Generic parser should degrade gracefully, never crash
g = parse_generic_html("<html><body><p>DCC rate is $12,345 per unit</p></body></html>", "t")
print(f"  {'OK  ' if g.ok and len(g.rates) == 1 else 'FAIL'} generic parser found "
      f"{len(g.rates)} candidate (expect 1)")
fails += not (g.ok and len(g.rates) == 1)

g2 = parse_generic_html("<html><body><p>nothing here</p></body></html>", "t")
print(f"  {'OK  ' if g2.ok and not g2.rates else 'FAIL'} generic parser handles empty page")
fails += not (g2.ok and not g2.rates)

print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' FAILURES'}")
