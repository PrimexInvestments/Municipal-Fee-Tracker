"""
Seed dataset for the Metro Vancouver development fee tracker.

Every rate here was pulled from an official or primary source on 2026-07-23.
The SOURCES registry is also what scrape_dev_fees.py reads to know where to look.
"""

VERIFIED = "2026-07-23"

# ---------------------------------------------------------------------------
# Source registry -- the scraper iterates over this.
# parser: which adapter in scrape_dev_fees.py handles the page
# ---------------------------------------------------------------------------
SOURCES = [
    {
        "id": "metro_van_dcc",
        "jurisdiction": "Metro Vancouver (regional)",
        "fee_types": "Water DCC, Liquid Waste DCC, Parkland DCC",
        "url": "https://metrovancouver.org/about-us/development-cost-charges",
        "parser": "metro_van_dcc",
        "format": "HTML tables",
        "reliability": "High - clean semantic tables",
        "update_cadence": "Jan 1 annually; ad hoc bylaw amendments",
    },
    {
        "id": "vancouver_dcl",
        "jurisdiction": "Vancouver",
        "fee_types": "City-wide DCL, Utilities DCL, Area-specific DCL",
        "url": "https://vancouver.ca/home-property-development/development-cost-levies.aspx",
        "parser": "vancouver_dcl",
        "format": "HTML + PDF bulletin",
        "reliability": "Medium - rates live in a linked PDF bulletin",
        "update_cadence": "Sept 30 annually",
    },
    {
        "id": "vancouver_dcl_bulletin",
        "jurisdiction": "Vancouver",
        "fee_types": "DCL rate schedule (authoritative)",
        "url": "https://guidelines.vancouver.ca/bulletins/bulletin-development-cost-levies.pdf",
        "parser": "pdf_rate_table",
        "format": "PDF",
        "reliability": "High - authoritative, but PDF parsing is brittle",
        "update_cadence": "Sept 30 annually",
    },
    {
        "id": "vancouver_opendata_dcl_areas",
        "jurisdiction": "Vancouver",
        "fee_types": "DCL district boundaries",
        "url": "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/development-cost-levy-dcl-areas/records",
        "parser": "opendatasoft_api",
        "format": "JSON API",
        "reliability": "High - proper REST API, refreshed weekly",
        "update_cadence": "Weekly extract",
    },
    {
        "id": "surrey_dcc",
        "jurisdiction": "Surrey",
        "fee_types": "DCC, area-specific DCC",
        "url": "https://www.surrey.ca/renovating-building-development/engineering-infrastructure/development-cost-charges",
        "parser": "generic_html",
        "format": "HTML + PDF schedules",
        "reliability": "Medium",
        "update_cadence": "Bylaw-driven, needs provincial approval",
    },
    {
        "id": "burnaby_dcc",
        "jurisdiction": "Burnaby",
        "fee_types": "DCC, density bonus",
        "url": "https://www.burnaby.ca/services-and-payments/building-and-development/development-cost-charges",
        "parser": "generic_html",
        "format": "HTML + PDF",
        "reliability": "Medium - verify URL, site restructured 2024",
        "update_cadence": "Annual",
    },
    {
        "id": "richmond_dcc",
        "jurisdiction": "Richmond",
        "fee_types": "DCC",
        "url": "https://www.richmond.ca/plandev/planning2/developmentcostcharges.htm",
        "parser": "generic_html",
        "format": "HTML",
        "reliability": "Medium",
        "update_cadence": "Annual",
    },
    {
        "id": "new_west_dcc",
        "jurisdiction": "New Westminster",
        "fee_types": "DCC",
        "url": "https://www.newwestcity.ca/business-and-development/development-cost-charges",
        "parser": "generic_html",
        "format": "HTML",
        "reliability": "Medium",
        "update_cadence": "Annual - new bylaw adopted 2026-01-12",
    },
    {
        "id": "coquitlam_dcc",
        "jurisdiction": "Coquitlam",
        "fee_types": "DCC",
        "url": "https://www.coquitlam.ca/291/Development-Cost-Charges",
        "parser": "generic_html",
        "format": "HTML",
        "reliability": "Medium",
        "update_cadence": "Annual",
    },
    {
        "id": "translink_dcc",
        "jurisdiction": "TransLink (regional)",
        "fee_types": "Transportation DCC",
        "url": "https://www.translink.ca/about-us/doing-business-with-translink/development-cost-charges",
        "parser": "generic_html",
        "format": "HTML",
        "reliability": "Medium",
        "update_cadence": "Annual",
    },
]

# ---------------------------------------------------------------------------
# Metro Vancouver regional DCCs -- applies on TOP of municipal fees everywhere
# Source: metrovancouver.org/about-us/development-cost-charges (fetched 2026-07-23)
# NOTE: these are the rates as published. A rollback bylaw is scheduled for
# adoption 2026-07-24 which reverts the Jan 1 2026 column to the Jan 1 2025 values.
# ---------------------------------------------------------------------------

# component -> {land_use: (2025, 2026, 2027)}
MV_WATER_DCC = {
    "Residential Lot Development Unit": (10952, 16926, 19714),
    "Townhouse Dwelling Unit": (9839, 15206, 17710),
    "Apartment Dwelling Unit": (6791, 10495, 12223),
    "Non-Residential (per sq ft)": (5.30, 8.19, 9.54),
}
MV_WATER_ASSIST = (0.45, 0.15, 0.01)

# sewerage_area -> {land_use: (2025, 2026, 2027)}
MV_LIQUID_WASTE_DCC = {
    "Vancouver Sewerage Area (VSA)": {
        "Residential Lot Development Unit": (10498, 11290, 12476),
        "Townhouse Dwelling Unit": (9593, 10316, 11400),
        "Apartment Dwelling Unit": (6298, 6772, 7484),
        "Non-Residential (per sq ft)": (5.30, 5.70, 6.30),
    },
    "North Shore Sewerage Area (NSSA)": {
        "Residential Lot Development Unit": (9760, 10478, 11557),
        "Townhouse Dwelling Unit": (8996, 9658, 10652),
        "Apartment Dwelling Unit": (6005, 6448, 7111),
        "Non-Residential (per sq ft)": (5.00, 5.37, 5.92),
    },
    "Lulu Island West Sewerage Area (LIWSA)": {
        "Residential Lot Development Unit": (5683, 6152, 6855),
        "Townhouse Dwelling Unit": (4927, 5333, 5943),
        "Apartment Dwelling Unit": (3516, 3806, 4241),
        "Non-Residential (per sq ft)": (2.55, 2.76, 3.08),
    },
    "Fraser Sewerage Area (FSA)": {
        "Residential Lot Development Unit": (11443, 12311, 13613),
        "Townhouse Dwelling Unit": (10015, 10775, 11914),
        "Apartment Dwelling Unit": (7302, 7855, 8686),
        "Non-Residential (per sq ft)": (5.41, 5.82, 6.43),
    },
}
MV_LW_ASSIST = (0.16, 0.10, 0.01)

MV_PARKLAND_DCC = {
    "Residential Lot Development Unit": (491, 981, 1943),
    "Townhouse Dwelling Unit": (442, 884, 1751),
    "Apartment Dwelling Unit": (303, 606, 1199),
    "Non-Residential (per sq ft)": (0.24, 0.48, 0.94),
}
MV_PARKLAND_ASSIST = (0.75, 0.50, 0.01)

# Metro Vancouver's OWN published total rows, transcribed as printed.
# These occasionally differ by $1 from the sum of the published components
# because MV rounds each component independently. The workbook reconciles
# the two rather than silently picking one.
MV_PUBLISHED_TOTAL = {
    "Vancouver Sewerage Area (VSA)": {
        "Residential Lot Development Unit": (21941, 29196, 34133),
        "Townhouse Dwelling Unit": (19874, 26406, 30861),
        "Apartment Dwelling Unit": (13392, 17873, 20906),
        "Non-Residential (per sq ft)": (10.84, 14.37, 16.78),
    },
    "North Shore Sewerage Area (NSSA)": {
        "Residential Lot Development Unit": (21203, 28385, 33214),
        "Townhouse Dwelling Unit": (19277, 25748, 30113),
        "Apartment Dwelling Unit": (13099, 17548, 20533),
        "Non-Residential (per sq ft)": (10.54, 14.04, 16.40),
    },
    "Lulu Island West Sewerage Area (LIWSA)": {
        "Residential Lot Development Unit": (17126, 24058, 28512),
        "Townhouse Dwelling Unit": (15208, 21423, 25404),
        "Apartment Dwelling Unit": (10610, 14906, 17663),
        "Non-Residential (per sq ft)": (8.09, 11.43, 13.56),
    },
    "Fraser Sewerage Area (FSA)": {
        "Residential Lot Development Unit": (22886, 30218, 35270),
        "Townhouse Dwelling Unit": (20296, 26865, 31375),
        "Apartment Dwelling Unit": (14396, 18956, 22108),
        "Non-Residential (per sq ft)": (10.95, 14.49, 16.91),
    },
}

LAND_USES = [
    "Residential Lot Development Unit",
    "Townhouse Dwelling Unit",
    "Apartment Dwelling Unit",
    "Non-Residential (per sq ft)",
]

SEWERAGE_AREAS = list(MV_LIQUID_WASTE_DCC.keys())

# Which municipalities sit in which sewerage area (for the calculator)
MUNI_TO_SEWERAGE = {
    "Vancouver": "Vancouver Sewerage Area (VSA)",
    "Burnaby": "Vancouver Sewerage Area (VSA)",
    "New Westminster": "Fraser Sewerage Area (FSA)",
    "Surrey": "Fraser Sewerage Area (FSA)",
    "Coquitlam": "Fraser Sewerage Area (FSA)",
    "Port Coquitlam": "Fraser Sewerage Area (FSA)",
    "Port Moody": "Fraser Sewerage Area (FSA)",
    "Delta": "Fraser Sewerage Area (FSA)",
    "Langley (City)": "Fraser Sewerage Area (FSA)",
    "Langley (Township)": "Fraser Sewerage Area (FSA)",
    "Maple Ridge": "Fraser Sewerage Area (FSA)",
    "Pitt Meadows": "Fraser Sewerage Area (FSA)",
    "White Rock": "Fraser Sewerage Area (FSA)",
    "Richmond": "Lulu Island West Sewerage Area (LIWSA)",
    "North Vancouver (City)": "North Shore Sewerage Area (NSSA)",
    "North Vancouver (District)": "North Shore Sewerage Area (NSSA)",
    "West Vancouver": "North Shore Sewerage Area (NSSA)",
}

# ---------------------------------------------------------------------------
# Vancouver DCL rates, from the City's own DCL Bulletin (last amended
# 2026-01-22), Table 1, effective 2025-12-10. Verified against the primary
# source 2026-07-23.
#
# These already reflect the 20% reduction Council approved 2025-12-10, which
# the bulletin states is expected to hold until 2026-09-30.
#
# band -> (city_wide_per_m2, utilities_per_m2)
# ---------------------------------------------------------------------------
VANCOUVER_DCL = {
    "Residential at or below 1.2 FSR / laneway": (49.88, 31.25),
    "Residential above 1.2 to 1.5 FSR": (107.34, 67.33),
    "Residential above 1.5 FSR": (214.89, 134.65),
    "Commercial and most other uses": (214.89, 67.33),
    "Industrial": (85.96, 26.91),
    "Mixed employment (light industrial)": (161.07, 50.47),
    "School (K-12)": (5.49, 5.49),
}
VANCOUVER_DCL_BANDS = list(VANCOUVER_DCL.keys())

# Layered area-specific DCLs, charged IN ADDITION to both city-wide DCLs.
# Only the <=1.2 FSR band is published as a single figure; higher bands vary.
VANCOUVER_AREA_DCL = {
    "False Creek Flats": 64.25,
    "South East False Creek": 198.64,
}

# TransLink regional DCC -- collected by the municipality on TransLink's behalf,
# on top of everything else. Source: Vancouver DCL Bulletin Appendix E.
# category -> (2025, 2026)
TRANSLINK_DCC = {
    "Single Family Dwelling": (3330, 3416),
    "Duplex": (2765, 2837),
    "Townhouse Dwelling": (2765, 2837),
    "Apartment": (1729, 1774),
    "Retail / Service (per sq ft)": (1.40, 1.44),
    "Office (per sq ft)": (1.13, 1.16),
    "Institutional (per sq ft)": (0.55, 0.56),
    "Industrial (per sq ft)": (0.33, 0.34),
}

# Maps the regional DCC land use to the matching TransLink category
LAND_USE_TO_TRANSLINK = {
    "Residential Lot Development Unit": "Single Family Dwelling",
    "Townhouse Dwelling Unit": "Townhouse Dwelling",
    "Apartment Dwelling Unit": "Apartment",
    "Non-Residential (per sq ft)": "Office (per sq ft)",
}

# ---------------------------------------------------------------------------
# Municipal-level fees (long format)
# cols: municipality, fee_program, land_use, rate, unit, effective, status,
#       bylaw, source_id, notes
# ---------------------------------------------------------------------------
MUNICIPAL_FEES = [
    # cols: municipality, program, land_use, rate, unit, effective, status,
    #       bylaw, source_id, next_review, review_basis, notes
    # --- VANCOUVER: verified against City DCL Bulletin (amended 2026-01-22) ---
    ("Vancouver", "City-wide DCL", "Residential at or below 1.2 FSR / laneway", 49.88,
     "$/m2 GFA", "2025-12-10", "In effect", "DCL By-law 12183", "vancouver_dcl_bulletin",
     "2026-09-30", "Annual DCL adjustment effective Sept 30 + Financing Growth update",
     "Includes the 20% reduction of 2025-12-10."),
    ("Vancouver", "Utilities DCL", "Residential at or below 1.2 FSR / laneway", 31.25,
     "$/m2 GFA", "2025-12-10", "In effect", "Utilities DCL By-law", "vancouver_dcl_bulletin",
     "2026-09-30", "Annual DCL adjustment effective Sept 30",
     "Combined with city-wide: $81.13/m2."),
    ("Vancouver", "City-wide DCL", "Residential above 1.2 to 1.5 FSR", 107.34,
     "$/m2 GFA", "2025-12-10", "In effect", "DCL By-law 12183", "vancouver_dcl_bulletin",
     "2026-09-30", "Annual DCL adjustment effective Sept 30", ""),
    ("Vancouver", "Utilities DCL", "Residential above 1.2 to 1.5 FSR", 67.33,
     "$/m2 GFA", "2025-12-10", "In effect", "Utilities DCL By-law", "vancouver_dcl_bulletin",
     "2026-09-30", "Annual DCL adjustment effective Sept 30", "Combined: $174.67/m2."),
    ("Vancouver", "City-wide DCL", "Residential above 1.5 FSR", 214.89,
     "$/m2 GFA", "2025-12-10", "In effect", "DCL By-law 12183", "vancouver_dcl_bulletin",
     "2026-09-30", "Annual DCL adjustment effective Sept 30",
     "Applies to most apartment and mid/high-rise projects."),
    ("Vancouver", "Utilities DCL", "Residential above 1.5 FSR", 134.65,
     "$/m2 GFA", "2025-12-10", "In effect", "Utilities DCL By-law", "vancouver_dcl_bulletin",
     "2026-09-30", "Annual DCL adjustment effective Sept 30",
     "Combined: $349.54/m2 - 4.3x the lowest residential band."),
    ("Vancouver", "City-wide DCL", "Commercial and most other uses", 214.89,
     "$/m2 GFA", "2025-12-10", "In effect", "DCL By-law 12183", "vancouver_dcl_bulletin",
     "2026-09-30", "Annual DCL adjustment effective Sept 30",
     "Default non-residential rate."),
    ("Vancouver", "Utilities DCL", "Commercial and most other uses", 67.33,
     "$/m2 GFA", "2025-12-10", "In effect", "Utilities DCL By-law", "vancouver_dcl_bulletin",
     "2026-09-30", "Annual DCL adjustment effective Sept 30", "Combined: $282.22/m2."),
    ("Vancouver", "City-wide DCL", "Industrial", 85.96, "$/m2 GFA", "2025-12-10",
     "In effect", "DCL By-law 12183", "vancouver_dcl_bulletin", "2026-09-30",
     "Annual DCL adjustment effective Sept 30", "I-2, M-1, M-1A, M-1B, M-2 districts."),
    ("Vancouver", "Utilities DCL", "Industrial", 26.91, "$/m2 GFA", "2025-12-10",
     "In effect", "Utilities DCL By-law", "vancouver_dcl_bulletin", "2026-09-30",
     "Annual DCL adjustment effective Sept 30", "Combined: $112.87/m2."),
    ("Vancouver", "City-wide DCL", "Mixed employment (light industrial)", 161.07,
     "$/m2 GFA", "2025-12-10", "In effect", "DCL By-law 12183", "vancouver_dcl_bulletin",
     "2026-09-30", "Annual DCL adjustment effective Sept 30",
     "IC-1, IC-2, I-1, I-1A, I-1B, I-1C, I-3, I-4 districts."),
    ("Vancouver", "Utilities DCL", "Mixed employment (light industrial)", 50.47,
     "$/m2 GFA", "2025-12-10", "In effect", "Utilities DCL By-law", "vancouver_dcl_bulletin",
     "2026-09-30", "Annual DCL adjustment effective Sept 30", "Combined: $211.54/m2."),
    ("Vancouver", "Area-specific DCL", "False Creek Flats (at or below 1.2 FSR)", 64.25,
     "$/m2 GFA", "2025-12-10", "In effect", "Area Specific DCL By-law 9418",
     "vancouver_dcl_bulletin", "2026-09-30", "Annual DCL adjustment effective Sept 30",
     "Layered ON TOP of both city-wide DCLs."),
    ("Vancouver", "Area-specific DCL", "South East False Creek (at or below 1.2 FSR)", 198.64,
     "$/m2 GFA", "2025-12-10", "In effect", "Area Specific DCL By-law 9418",
     "vancouver_dcl_bulletin", "2026-09-30", "Annual DCL adjustment effective Sept 30",
     "Layered ON TOP of both city-wide DCLs."),
    ("Vancouver", "Amenity Cost Charge (ACC)", "Residential at or below 1.2 FAR", 2.32,
     "$/sq ft", "2026-09-30", "Proposed - not adopted", "Draft ACC By-law", "vancouver_dcl",
     "2026-09-30", "Bylaw takes effect Sept 30 2026 if adopted",
     "NOT YET IN FORCE. Partly replaces negotiated CACs."),
    ("Vancouver", "Amenity Cost Charge (ACC)", "Industrial", 1.20, "$/sq ft", "2026-09-30",
     "Proposed - not adopted", "Draft ACC By-law", "vancouver_dcl", "2026-09-30",
     "Bylaw takes effect Sept 30 2026 if adopted", "NOT YET IN FORCE."),
    ("Vancouver", "Amenity Cost Charge (ACC)", "Mixed-employment light industrial", 2.25,
     "$/sq ft", "2026-09-30", "Proposed - not adopted", "Draft ACC By-law", "vancouver_dcl",
     "2026-09-30", "Bylaw takes effect Sept 30 2026 if adopted", "NOT YET IN FORCE."),
    ("Vancouver", "Amenity Cost Charge (ACC)", "Commercial and other", 3.00, "$/sq ft",
     "2026-09-30", "Proposed - not adopted", "Draft ACC By-law", "vancouver_dcl",
     "2026-09-30", "Bylaw takes effect Sept 30 2026 if adopted",
     "NOT YET IN FORCE. High-density residential ACC phases in at half rate yr 1."),

    # --- BURNABY: verified against burnaby.ca rate table, Bylaws 14645/14646 ---
    ("Burnaby", "DCC", "Low density residential (SFD / duplex)", 54870, "$/unit",
     "2024-07-01", "In effect", "DCC Bylaw 14645", "burnaby_dcc", "2027-01-01",
     "No announced update; review annually",
     "Transportation 16,858 + water 2,740 + drainage 5,734 + sewer 3,491 + parks 20,632 + fire 5,415."),
    ("Burnaby", "ACC", "Low density residential (SFD / duplex)", 26963, "$/unit",
     "2024-07-01", "In effect", "ACC Bylaw 14646", "burnaby_dcc", "2027-01-01",
     "No announced update; review annually", "Total DCC + ACC: $81,833/unit."),
    ("Burnaby", "DCC", "Medium density residential (townhouse / multiplex)", 37423,
     "$/unit", "2024-07-01", "In effect", "DCC Bylaw 14645", "burnaby_dcc", "2027-01-01",
     "No announced update; review annually",
     "Includes laneway, townhouse, rowhouse, multiplex."),
    ("Burnaby", "ACC", "Medium density residential (townhouse / multiplex)", 18874,
     "$/unit", "2024-07-01", "In effect", "ACC Bylaw 14646", "burnaby_dcc", "2027-01-01",
     "No announced update; review annually", "Total DCC + ACC: $56,297/unit."),
    ("Burnaby", "DCC", "High density residential (apartment)", 25360, "$/unit",
     "2024-07-01", "In effect", "DCC Bylaw 14645", "burnaby_dcc", "2027-01-01",
     "No announced update; review annually", "Units off a common corridor."),
    ("Burnaby", "ACC", "High density residential (apartment)", 13481, "$/unit",
     "2024-07-01", "In effect", "ACC Bylaw 14646", "burnaby_dcc", "2027-01-01",
     "No announced update; review annually", "Total DCC + ACC: $38,841/unit."),
    ("Burnaby", "DCC", "Commercial", 259.06, "$/m2 GFA", "2024-07-01", "In effect",
     "DCC Bylaw 14645", "burnaby_dcc", "2027-01-01", "No announced update; review annually",
     "Plus ACC $60.67/m2. Total $319.73/m2."),
    ("Burnaby", "DCC", "Industrial", 111.97, "$/m2 GFA", "2024-07-01", "In effect",
     "DCC Bylaw 14645", "burnaby_dcc", "2027-01-01", "No announced update; review annually",
     "Plus ACC $40.44/m2. Total $152.41/m2. No parks component."),
    ("Burnaby", "DCC", "Institutional", 183.40, "$/m2 GFA", "2024-07-01", "In effect",
     "DCC Bylaw 14645", "burnaby_dcc", "2027-01-01", "No announced update; review annually",
     "Plus ACC $60.67/m2. Total $244.07/m2."),
    ("Burnaby", "Density bonus (CBB)", "R6/R7/R8 market strata - SW quadrant", 185,
     "$/sq ft", "2025-10-01", "In effect", "Community Benefit Bonus Bylaw", "burnaby_dcc",
     "2026-10-01", "CBB rates updated annually",
     "Highest quadrant. NW $150, NE $140, SE $140. Market rental is lower."),
    ("Burnaby", "Density bonus (CBB)", "R6/R7/R8 market rental - SW quadrant", 148,
     "$/sq ft", "2025-10-01", "In effect", "Community Benefit Bonus Bylaw", "burnaby_dcc",
     "2026-10-01", "CBB rates updated annually", "NW $113, NE $105, SE $105."),

    # --- SURREY: in-force bylaw is still 21174 (2024). 2026 rates NOT in force. ---
    ("Surrey", "DCC", "See Bylaw 21174 schedule", 0, "varies", "2024-05-15",
     "In effect - rates not loaded", "DCC Bylaw 21174", "surrey_dcc", "2026-09-30",
     "2026 bylaw awaiting Inspector of Municipalities approval",
     "Surrey's site names Bylaw 21174 (in effect 2024-05-15) as current. The rate "
     "schedule is in a PDF that blocks automated access - read it manually. Rates "
     "deliberately left at 0 rather than carrying an unverified number."),
    ("Surrey", "DCC (proposed)", "Single / small-scale multi-unit (SSMUH)", 51633,
     "$/unit", "2026-05-11", "Proposed - not in force", "2026 DCC Bylaw", "surrey_dcc",
     "2026-09-30", "Awaiting provincial approval",
     "Three readings 2026-05-11, sent to Inspector of Municipalities. Down from $55,260."),
    ("Surrey", "DCC (proposed)", "Low-rise residential", 30.72, "$/sq ft", "2026-05-11",
     "Proposed - not in force", "2026 DCC Bylaw", "surrey_dcc", "2026-09-30",
     "Awaiting provincial approval", "Down from $33.47/sq ft."),
    ("Surrey", "DCC (proposed)", "High-rise residential", 30.30, "$/sq ft", "2026-05-11",
     "Proposed - not in force", "2026 DCC Bylaw", "surrey_dcc", "2026-09-30",
     "Awaiting provincial approval", "Down from $33.18/sq ft."),

    # --- Not yet verified: no rates carried rather than wrong ones ---
    ("Richmond", "DCC", "(not yet verified)", 0, "varies", "", "Not verified",
     "", "richmond_dcc", "2026-08-01", "Needs a primary-source pass",
     "No rates loaded. Do not assume zero - go read the bylaw."),
    ("New Westminster", "DCC", "(not yet verified)", 0, "varies", "2026-01-12",
     "Not verified", "2026 DCC Bylaw", "new_west_dcc", "2026-08-01",
     "Needs a primary-source pass",
     "New bylaw adopted 2026-01-12 adding fire and police categories; rates rose. Not loaded."),
    ("Coquitlam", "DCC", "(not yet verified)", 0, "varies", "", "Not verified",
     "", "coquitlam_dcc", "2026-08-01", "Needs a primary-source pass", "No rates loaded."),
    ("Langley (Township)", "DCC", "(not yet verified)", 0, "varies", "", "Not verified",
     "", None, "2026-08-01", "Needs a primary-source pass",
     "Earlier $87,615 figure came from a Surrey comparator report, not the Township "
     "bylaw. Removed rather than carried unverified."),
]

# ---------------------------------------------------------------------------
# Things in flight -- the reason a static sheet goes stale fast
# ---------------------------------------------------------------------------
PENDING_CHANGES = [
    ("2026-07-24", "Metro Vancouver", "DCC rollback bylaw adoption",
     "Board votes to roll 2026 rates back to 2025 levels, reduce 2027 increases, and defer "
     "the 1% assist factor from 2027 to 2029. Province approved the request in early July. "
     "If adopted, revised rates take effect same day. No rebates or retroactive adjustment "
     "for applications already in stream.",
     "HIGH - changes every regional DCC line in this workbook",
     "https://metrovancouver.org/about-us/development-cost-charges"),
    ("2026-09-30", "Vancouver", "Amenity Cost Charge By-law takes effect",
     "New city-wide ACC replaces much of the negotiated CAC system. In-stream applications "
     "filed before this date get up to 5 years of protection. ACC credit mechanism proposed "
     "for projects with existing secured CAC obligations to avoid double-charging.",
     "HIGH - new fee category, structural change to how Vancouver charges",
     "https://vancouver.ca/home-property-development/development-cost-levies.aspx"),
    ("2026-09-30", "Vancouver", "Updated DCL By-law takes effect",
     "Staff recommend the 20% temporary DCL reduction be revisited as part of the same "
     "Financing Growth package. Current $49.88/m2 and $39.06/m2 rates may change.",
     "HIGH - affects the two headline Vancouver rates",
     "https://vancouver.ca/home-property-development/development-cost-levies.aspx"),
    ("TBD 2026", "Surrey", "2026 DCC Bylaw provincial approval",
     "Bylaw given three readings 2026-05-11 and sent to the Inspector of Municipalities. "
     "Rates in this workbook are the proposed ones and are not yet in force.",
     "MEDIUM - rates listed are proposed, not adopted",
     "https://www.surrey.ca/renovating-building-development/engineering-infrastructure/development-cost-charges"),
    ("2027-01-01", "Metro Vancouver", "Step 3 DCC rates",
     "Originally legislated Step 3 increase. Being reduced as part of the July 2026 "
     "amendment, so the 2027 column here will need re-reading after the vote.",
     "MEDIUM - forward-looking column",
     "https://metrovancouver.org/about-us/development-cost-charges"),
    ("2028-01-01", "Metro Vancouver", "New DCC program rates",
     "Full DCC program update underway since 2025, integrated with the Capital Plan review. "
     "Proposed rates go to the Board in May 2026; new rates take effect 2028.",
     "LOW - far out, but will supersede everything",
     "https://metrovancouver.org/about-us/budgets-and-financial-plans/development-cost-charge-program-update"),
]
