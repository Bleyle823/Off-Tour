"""Nairobi National Park profile (conservation enablement)."""

PARK_ID = "nairobi_national_park"
DISPLAY_NAME = "Nairobi National Park"

# Named zones for sim / Webots (approximate placeholders).
EXCLUSION_ZONES = [
    {"id": "rhino_sanctuary", "note": "No flights; no public data"},
    {"id": "jkia_approach_buffer", "note": "KCAA + KAA coordination required"},
]

CONSERVATION_PRIORITIES = [
    "snaring along Mbagathi and dispersal edges",
    "rhino dispersal surveillance (KWS only)",
    "southern HWC buffer monitoring",
    "fence integrity",
    "dry-season bushfire watch",
]
