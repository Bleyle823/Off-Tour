"""Nairobi National Park profile (conservation enablement)."""

PARK_ID = "nairobi_national_park"
DISPLAY_NAME = "Nairobi National Park"

# Named zones for sim / Webots (approximate placeholders).
EXCLUSION_ZONES = [
    {"id": "rhino_sanctuary", "note": "No entry; no public live feed"},
]

# Placeholder circuit ids. Replace with the warden's current self-drive map.
DESIGNATED_PATHS = [
    {
        "id": "self_drive_circuit_a",
        "note": "Savannah sim loop. Waypoints: config/webots/off_tour_waypoints.json. Not a KWS-approved circuit.",
    },
]

CONSERVATION_PRIORITIES = [
    "snaring along Mbagathi and dispersal edges",
    "rhino dispersal surveillance (KWS only)",
    "southern HWC buffer monitoring",
    "fence integrity",
    "dry-season bushfire watch",
]
