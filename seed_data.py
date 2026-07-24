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
    "Residential Lot Development Unit": (10952, 10952, 15532),
    "Townhouse Dwelling Unit": (9839, 9839, 13954),
    "Apartment Dwelling Unit": (6791, 6791, 9630),
    "Non-Residential (per sq ft)": (5.30, 5.30, 7.51),
}
MV_WATER_ASSIST = (0.45, 0.15, 0.01)

# sewerage_area -> {land_use: (2025, 2026, 2027)}
MV_LIQUID_WASTE_DCC = {
    "Vancouver Sewerage Area (VSA)": {
        "Residential Lot Development Unit": (10498, 10498, 11553),
        "Townhouse Dwelling Unit": (9593, 9593, 10557),
        "Apartment Dwelling Unit": (6298, 6298, 6930),
        "Non-Residential (per sq ft)": (5.30, 5.30, 5.83),
    },
    "North Shore Sewerage Area (NSSA)": {
        "Residential Lot Development Unit": (9760, 9760, 10718),
        "Townhouse Dwelling Unit": (8996, 8996, 9879),
        "Apartment Dwelling Unit": (6005, 6005, 6595),
        "Non-Residential (per sq ft)": (5, 5, 5.49),
    },
    "Lulu Island West Sewerage Area (LIWSA)": {
        "Residential Lot Development Unit": (5683, 5683, 6308),
        "Townhouse Dwelling Unit": (4927, 4927, 5469),
        "Apartment Dwelling Unit": (3516, 3516, 3903),
        "Non-Residential (per sq ft)": (2.55, 2.55, 2.83),
    },
    "Fraser Sewerage Area (FSA)": {
        "Residential Lot Development Unit": (11443, 11443, 12601),
        "Townhouse Dwelling Unit": (10015, 10015, 11028),
        "Apartment Dwelling Unit": (7302, 7302, 8040),
        "Non-Residential (per sq ft)": (5.41, 5.41, 5.95),
    },
}
MV_LW_ASSIST = (0.16, 0.10, 0.01)

MV_PARKLAND_DCC = {
    "Residential Lot Development Unit": (491, 491, 1237),
    "Townhouse Dwelling Unit": (442, 442, 1114),
    "Apartment Dwelling Unit": (303, 303, 763),
    "Non-Residential (per sq ft)": (0.24, 0.24, 0.60),
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


# ===========================================================================
# VANCOUVER ISLAND MUNICIPALITIES
# ---------------------------------------------------------------------------
# Structurally different from Metro Vancouver: no regional DCC umbrella in
# force, and charges are split by SERVICE (transportation, water, drainage,
# sewer, parks) rather than water / liquid-waste / parkland. Each city is its
# own bylaw. Verified from primary bylaw PDFs except where marked UNVERIFIED.
#
# Rates researched 2026-07-24. Victoria + Courtenay + Colwood + Langford +
# Nanaimo(2022) confirmed from official sources; Duncan + Comox flagged.
# ===========================================================================

# muni -> {landUse: {component: rate}}  (component-level, for the detail view)
ISLAND_DCC = {
    "Victoria": {
        "Low density residential": {"unit": "$/lot or unit", "Transportation": 9254.76,
            "Water": 4071.05, "Drainage": 571.55, "Sewer": 2104.61, "Parks": 8580.10,
            "total": 24582.06},
        "Medium density residential": {"unit": "$/unit", "Transportation": 4212.51,
            "Water": 2770.24, "Drainage": 276.25, "Sewer": 1432.13, "Parks": 5838.53,
            "total": 14529.66},
        "High density residential": {"unit": "$/unit", "Transportation": 3957.21,
            "Water": 1686.23, "Drainage": 138.12, "Sewer": 871.73, "Parks": 3553.89,
            "total": 10207.18},
        "Commercial": {"unit": "$/m2 GFA", "Transportation": 63.83, "Water": 13.25,
            "Drainage": 1.52, "Sewer": 6.85, "Parks": 5.58, "total": 91.03},
        "Industrial": {"unit": "$/m2 GFA", "Transportation": 19.15, "Water": 5.42,
            "Drainage": 1.05, "Sewer": 2.80, "Parks": 2.28, "total": 30.70},
        "Institutional": {"unit": "$/m2 GFA", "Transportation": 63.83, "Water": 13.25,
            "Drainage": 1.52, "Sewer": 6.85, "Parks": 5.58, "total": 91.03},
    },
    "Courtenay": {
        "Low density residential": {"unit": "$/lot or unit", "total": 21832.0},
        "Medium density residential": {"unit": "$/unit", "total": 12278.0},
        "High density residential": {"unit": "$/m2 GFA", "total": 141.09},
        "Commercial": {"unit": "$/m2 GFA", "total": 91.32},
        "Industrial": {"unit": "$/m2 GFA", "total": 17.10},
        "Institutional": {"unit": "$/m2 GFA", "total": 73.31},
    },
    "Nanaimo": {
        "Low density residential": {"unit": "$/lot", "Sewer": 1787.04, "Drainage": 75.94,
            "Water": 5925.89, "Parks": 1249.32, "Transportation": 5824.08, "total": 14862.27},
        "High density residential": {"unit": "$/m2 GFA", "Sewer": 10.77, "Drainage": 0.38,
            "Water": 35.71, "Parks": 7.53, "Transportation": 35.09, "total": 89.10},
        "Commercial": {"unit": "$/m2 GFA", "total": 77.42},
        "Industrial": {"unit": "$/m2 GFA", "total": 19.75},
    },
    # Colwood + Langford: multiple component bylaws summed to a single-family total.
    "Colwood": {
        "Low density residential": {"unit": "$/lot", "Transportation": 8142.09,
            "Parks": 5707.01, "Sewer": 3077.0, "total": 16926.10},
        "Medium density residential": {"unit": "$/unit", "Transportation": 5268.41,
            "Parks": 4993.64, "Sewer": 2095.0, "total": 12357.05},
        "High density residential": {"unit": "$/unit", "Transportation": 4949.11,
            "Parks": 3210.19, "Sewer": 1178.0, "total": 9337.30},
    },
    "Langford": {
        "Low density residential": {"unit": "$/lot", "Transportation": 5876.0,
            "Drainage": 1655.0, "Parks": 3357.0, "Sewer": 495.0, "total": 11383.0},
        "Medium density residential": {"unit": "$/unit", "Transportation": 3865.0,
            "Drainage": 1028.0, "Parks": 2078.0, "Sewer": 371.25, "total": 7342.25},
        "High density residential": {"unit": "$/unit", "Transportation": 3092.39,
            "Drainage": 635.0, "Parks": 1438.0, "Sewer": 331.65, "total": 5497.04},
    },
}

# Regional water DCCs that layer on top of the municipal charge (CRD Juan de
# Fuca, collected today) and the pending ones.
ISLAND_REGIONAL = {
    "CRD Juan de Fuca Water (in force)": {
        "applies": ["Colwood", "Langford"],
        "Low density residential": 2796.0, "Medium density residential": 2446.0,
        "High density residential": 1573.0, "unit": "$/lot or unit"},
}

# Island municipal fee rows in the standard 12-field schema, appended to
# MUNICIPAL_FEES so they flow through the register, staleness check and scraper.
ISLAND_FEES = [
    # --- VICTORIA (verified, Bylaw 24-053, in force Nov 2024) ---
    ("Victoria", "DCC", "Low density residential", 24582.06, "$/lot or unit", "2024-11-14",
     "In effect", "DCC Bylaw 24-053", "victoria_dcc", "2027-01-01",
     "5-year bylaw cycle", "Transportation 9,254.76 + water 4,071.05 + drainage 571.55 "
     "+ sewer 2,104.61 + parks 8,580.10. Exempt: <4 units, <29m2, work <$50k."),
    ("Victoria", "DCC", "Medium density residential", 14529.66, "$/unit", "2024-11-14",
     "In effect", "DCC Bylaw 24-053", "victoria_dcc", "2027-01-01", "5-year bylaw cycle", ""),
    ("Victoria", "DCC", "High density residential", 10207.18, "$/unit", "2024-11-14",
     "In effect", "DCC Bylaw 24-053", "victoria_dcc", "2027-01-01", "5-year bylaw cycle", ""),
    ("Victoria", "DCC", "Commercial / Institutional", 91.03, "$/m2 GFA", "2024-11-14",
     "In effect", "DCC Bylaw 24-053", "victoria_dcc", "2027-01-01", "5-year bylaw cycle", ""),
    ("Victoria", "DCC", "Industrial", 30.70, "$/m2 GFA", "2024-11-14",
     "In effect", "DCC Bylaw 24-053", "victoria_dcc", "2027-01-01", "5-year bylaw cycle", ""),

    # --- COURTENAY (verified, Bylaw 3191, in force Apr 30 2026) ---
    ("Courtenay", "DCC", "Low density residential", 21832.0, "$/lot or unit", "2026-04-30",
     "In effect", "DCC Bylaw 3191", "courtenay_dcc", "2027-04-30",
     "Adopted Apr 2026; 1% MAF, 20-yr horizon",
     "Funds transportation, water, drainage, sanitary, parks, fire. Plus CVRD sewer DCC. "
     "Courtenay also adopted an ACC effective same date."),
    ("Courtenay", "DCC", "Medium density residential", 12278.0, "$/unit", "2026-04-30",
     "In effect", "DCC Bylaw 3191", "courtenay_dcc", "2027-04-30", "Adopted Apr 2026", ""),
    ("Courtenay", "DCC", "High density residential", 141.09, "$/m2 GFA", "2026-04-30",
     "In effect", "DCC Bylaw 3191", "courtenay_dcc", "2027-04-30", "Adopted Apr 2026", ""),
    ("Courtenay", "DCC", "Commercial", 91.32, "$/m2 GFA", "2026-04-30",
     "In effect", "DCC Bylaw 3191", "courtenay_dcc", "2027-04-30", "Adopted Apr 2026", ""),
    ("Courtenay", "DCC", "Industrial", 17.10, "$/m2 GFA", "2026-04-30",
     "In effect", "DCC Bylaw 3191", "courtenay_dcc", "2027-04-30", "Adopted Apr 2026", ""),
    ("Courtenay", "DCC", "Institutional", 73.31, "$/m2 GFA", "2026-04-30",
     "In effect", "DCC Bylaw 3191", "courtenay_dcc", "2027-04-30", "Adopted Apr 2026", ""),

    # --- NANAIMO (verified current, Bylaw 7252 2022; big increase pending) ---
    ("Nanaimo", "DCC", "Low density residential (single family)", 14862.27, "$/lot", "2022-12-07",
     "In effect", "DCC Bylaw 7252", "nanaimo_dcc", "2027-01-01",
     "Bylaw 7438 replaces this Jan 2027 (~$42,887/lot)",
     "City portion. RDN Southern Wastewater adds $4,622.37/lot -> $19,484.64 total. "
     "Non-profit rental gets 50% reduction."),
    ("Nanaimo", "DCC", "High density residential", 89.10, "$/m2 GFA", "2022-12-07",
     "In effect", "DCC Bylaw 7252", "nanaimo_dcc", "2027-01-01",
     "Bylaw 7438 replaces this Jan 2027", ""),
    ("Nanaimo", "DCC", "Commercial / Institutional", 77.42, "$/m2 GFA", "2022-12-07",
     "In effect", "DCC Bylaw 7252", "nanaimo_dcc", "2027-01-01", "Bylaw 7438 pending", ""),
    ("Nanaimo", "DCC", "Industrial", 19.75, "$/m2 GFA", "2022-12-07",
     "In effect", "DCC Bylaw 7252", "nanaimo_dcc", "2027-01-01", "Bylaw 7438 pending", ""),
    ("Nanaimo", "DCC (proposed)", "Low density residential", 42887.29, "$/lot", "2027-01-01",
     "Proposed - not in force", "DCC Bylaw 7438", "nanaimo_dcc", "2027-01-01",
     "First 3 readings Apr 2026; adoption planned Jan 2027",
     "Scenario 2, 1% MAF. Nearly 3x current. With ACC $48,165.73. Plus South Nanaimo "
     "area-specific transportation DCC where applicable."),

    # --- PARKSVILLE (verified brochure; City + RDN combined) ---
    ("Parksville", "DCC", "Residential subdivision (1-2 units/lot)", 28344.74, "$/lot", "2023-06-01",
     "In effect", "DCC Bylaw 1437", "parksville_dcc", "2026-12-01",
     "RDN Northern sewer DCC under review (~37-39% increase)",
     "City $14,489.99 + RDN Northern sewer $13,854.75. RDN portion increasing."),
    ("Parksville", "DCC", "Multi-family low density", 207.97, "$/m2 GFA", "2023-06-01",
     "In effect", "DCC Bylaw 1437", "parksville_dcc", "2026-12-01", "RDN portion under review",
     "Combined City + RDN."),
    ("Parksville", "DCC", "Commercial", 153.43, "$/m2 GFA", "2023-06-01",
     "In effect", "DCC Bylaw 1437", "parksville_dcc", "2026-12-01", "RDN portion under review", ""),
    ("Parksville", "DCC", "Industrial", 120.54, "$/m2 GFA", "2023-06-01",
     "In effect", "DCC Bylaw 1437", "parksville_dcc", "2026-12-01", "RDN portion under review", ""),

    # --- LANGFORD (verified summary sheet; component bylaws summed) ---
    ("Langford", "DCC", "Low density residential (single family)", 11383.0, "$/lot", "2023-09-05",
     "In effect", "Bylaws 2021/2022/2023/2024/1600", "langford_dcc", "2026-12-01",
     "Multiple component bylaws; review annually",
     "Roads 5,876 + drainage 1,655 + parks 3,357 + sewer ISIF 495. No municipal water DCC "
     "(CRD Juan de Fuca water DCC $2,796 applies on top)."),
    ("Langford", "DCC", "Medium density residential", 7342.25, "$/unit", "2023-09-05",
     "In effect", "Bylaws 2021-2024/1600", "langford_dcc", "2026-12-01", "Component bylaws", ""),
    ("Langford", "DCC", "High density residential", 5497.04, "$/unit", "2023-09-05",
     "In effect", "Bylaws 2021-2024/1600", "langford_dcc", "2026-12-01", "Component bylaws", ""),

    # --- COLWOOD (verified consolidated PDF; component bylaws summed) ---
    ("Colwood", "DCC", "Low density residential (single family)", 16926.10, "$/lot", "2024-10-28",
     "In effect", "Bylaws 1836/1990/2037/1500", "colwood_dcc", "2026-12-01",
     "Multiple component bylaws; review annually",
     "Roads 8,142.09 + parks acq 2,900.53 + park impr 2,806.48 + sewer enhancement 3,077. "
     "No municipal water DCC (CRD Juan de Fuca $2,796 applies on top)."),
    ("Colwood", "DCC", "Medium density residential", 12357.05, "$/unit", "2024-10-28",
     "In effect", "Bylaws 1836/1990/2037/1500", "colwood_dcc", "2026-12-01", "Component bylaws", ""),
    ("Colwood", "DCC", "High density residential", 9337.30, "$/unit", "2024-10-28",
     "In effect", "Bylaws 1836/1990/2037/1500", "colwood_dcc", "2026-12-01", "Component bylaws", ""),

    # --- COMOX (UNVERIFIED - bylaw PDF blocked; draft figures only) ---
    ("Comox", "DCC", "Low density residential", 30792.0, "$/lot", "2026-01-01",
     "Needs verification", "DCC Bylaw 2053", "comox_dcc", "2026-08-15",
     "Adopted rates unconfirmed - verify against bylaw PDF",
     "UNVERIFIED. This is the June 2025 DRAFT figure; whether adopted Bylaw 2053 matches "
     "is unconfirmed (PDF blocked automated access). Plus Comox ACC and CVRD water/sewer DCCs."),
    ("Comox", "DCC", "Medium density residential", 14466.0, "$/unit", "2026-01-01",
     "Needs verification", "DCC Bylaw 2053", "comox_dcc", "2026-08-15",
     "Draft figure - verify", "UNVERIFIED draft."),
    ("Comox", "DCC", "High density residential", 160.49, "$/m2 GFA", "2026-01-01",
     "Needs verification", "DCC Bylaw 2053", "comox_dcc", "2026-08-15",
     "Draft figure - verify", "UNVERIFIED draft."),

    # --- DUNCAN (UNVERIFIED - bylaw PDF blocked; news figures only) ---
    ("Duncan", "DCC", "Single family residential", 7814.0, "$/lot", "2023-07-21",
     "Needs verification", "DCC Bylaw 3234", "duncan_dcc", "2026-08-15",
     "Rates from news, not bylaw - verify against PDF",
     "UNVERIFIED. Figure from Cowichan Valley Citizen at introduction, not the bylaw text. "
     "Up to 50% reduction for multi-family meeting density targets, +25% for sustainability."),
    ("Duncan", "DCC", "Townhouse", 5412.0, "$/unit", "2023-07-21",
     "Needs verification", "DCC Bylaw 3234", "duncan_dcc", "2026-08-15",
     "News figure - verify", "UNVERIFIED."),
    ("Duncan", "DCC", "Apartment", 3986.0, "$/unit", "2023-07-21",
     "Needs verification", "DCC Bylaw 3234", "duncan_dcc", "2026-08-15",
     "News figure - verify", "UNVERIFIED."),
]

# Fold Island rows into the main list the site + scraper already read.
MUNICIPAL_FEES = MUNICIPAL_FEES + ISLAND_FEES

# Island sources for the scraper's Sources tab + staleness targeting.
ISLAND_SOURCES = [
    {"id": "victoria_dcc", "jurisdiction": "Victoria", "fee_types": "DCC (all services)",
     "url": "https://www.victoria.ca/city-government/bylaws/development-cost-charges",
     "parser": "generic_html", "format": "HTML + PDF bylaw",
     "reliability": "High - verified from Bylaw 24-053 PDF", "update_cadence": "5-year cycle"},
    {"id": "courtenay_dcc", "jurisdiction": "Courtenay", "fee_types": "DCC + ACC",
     "url": "https://www.courtenay.ca/dcc", "parser": "generic_html",
     "format": "HTML", "reliability": "High - verified from official page",
     "update_cadence": "Adopted Apr 2026"},
    {"id": "nanaimo_dcc", "jurisdiction": "Nanaimo", "fee_types": "DCC (+ RDN sewer)",
     "url": "https://www.nanaimo.ca/your-government/projects/development-cost-charge-bylaw-project",
     "parser": "generic_html", "format": "HTML + PDF",
     "reliability": "Medium - current verified, Bylaw 7438 pending Jan 2027",
     "update_cadence": "Major update Jan 2027"},
    {"id": "parksville_dcc", "jurisdiction": "Parksville", "fee_types": "DCC (City + RDN)",
     "url": "http://www.parksville.ca/cms.asp?wpID=476", "parser": "generic_html",
     "format": "HTML brochure", "reliability": "Medium - RDN portion under review",
     "update_cadence": "RDN sewer DCC increasing"},
    {"id": "langford_dcc", "jurisdiction": "Langford", "fee_types": "DCC (component bylaws)",
     "url": "https://langford.ca/wp-content/uploads/2020/10/DCC-Summary-Sheet.pdf",
     "parser": "pdf_rate_table", "format": "PDF summary sheet",
     "reliability": "Medium - multiple bylaws, verified 2025-05", "update_cadence": "Annual"},
    {"id": "colwood_dcc", "jurisdiction": "Colwood", "fee_types": "DCC (component bylaws)",
     "url": "https://www.colwood.ca/sites/default/files/2025-01/DEVELOPMENT%20COST%20CHARGES%20(January%202025).pdf",
     "parser": "pdf_rate_table", "format": "PDF", "reliability": "Medium - verified Jan 2025",
     "update_cadence": "Annual"},
    {"id": "comox_dcc", "jurisdiction": "Comox", "fee_types": "DCC + ACC",
     "url": "https://www.comox.ca/dcc", "parser": "generic_html",
     "format": "HTML + PDF (blocked)", "reliability": "LOW - rates unverified, PDF blocked",
     "update_cadence": "Bylaw 2053 adopted 2026"},
    {"id": "duncan_dcc", "jurisdiction": "Duncan", "fee_types": "DCC",
     "url": "https://duncan.ca/city-hall/planning-and-development/development-cost-charges/",
     "parser": "generic_html", "format": "HTML + PDF (blocked)",
     "reliability": "LOW - rates from news, unverified", "update_cadence": "Bylaw 3234 (2023)"},
]
SOURCES = SOURCES + ISLAND_SOURCES

# Island-relevant upcoming changes for the timeline / staleness banner.
ISLAND_PENDING = [
    ("2027-01-01", "Nanaimo", "Bylaw 7438 takes effect",
     "Low density residential DCC rises from ~$14,862 to ~$42,887/lot (nearly 3x), plus a "
     "new ACC and a South Nanaimo area-specific transportation DCC. First three readings "
     "given April 2026; adoption planned January 2027.",
     "HIGH - triples Nanaimo's single-family charge",
     "https://www.nanaimo.ca/your-government/projects/development-cost-charge-bylaw-project"),
    ("2027-04-02", "CRD (regional)", "Regional Water Supply DCC starts",
     "New CRD-wide water DCC (~$9,044/single-family lot, $5,087/apartment) layering on top "
     "of municipal charges across Victoria, Langford, Colwood and other CRD members. Three "
     "readings Feb 2026, with the Inspector of Municipalities; delayed start April 2 2027.",
     "HIGH - new regional charge across Greater Victoria",
     "https://getinvolved.crd.bc.ca/water-supply-dcc"),
    ("2026-06-01", "Comox Valley (regional)", "CVRD sewer fee changes",
     "CVRD Bylaw 71 sewerage service fee changes take effect, with sewer DCCs increasing. "
     "Affects Courtenay and Comox, which collect the CVRD sewer DCC.",
     "MEDIUM - regional sewer component rising",
     "https://www.comoxvalleyrd.ca/services/sewer/sewerage-fees-charges"),
]
PENDING_CHANGES = PENDING_CHANGES + ISLAND_PENDING

print("Island data appended to seed_data.py structures")
