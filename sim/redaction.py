"""Stream-style data packages before signing (field rules)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Set

# Species whose coordinates must never appear in a public package.
PROTECTED_SPECIES: Set[str] = {"black_rhino", "white_rhino", "rhino"}


def build_detection_package(
    raw: Dict[str, Any],
    audience: str,
) -> Dict[str, Any]:
    """Return a copy safe to sign for the given audience.

    audience: "public" | "guide" | "kws" | "participant"
    """
    out = deepcopy(raw)
    species = str(out.get("species", "")).lower().replace(" ", "_")

    if species in PROTECTED_SPECIES:
        out.pop("lat", None)
        out.pop("lon", None)
        out["location"] = "redacted"
        out["delay_minutes"] = None if audience == "kws" else 9999
        return out

    if audience == "public":
        out.pop("lat", None)
        out.pop("lon", None)
        out["location"] = "coarse_grid_only"
    elif audience == "guide":
        if "lat" in out and "lon" in out:
            out["lat"] = round(float(out["lat"]), 2)
            out["lon"] = round(float(out["lon"]), 2)
        out["delay_minutes"] = 30
    elif audience == "participant":
        # Session buyer sees live coarse location for non-protected species only.
        if "lat" in out and "lon" in out:
            out["lat"] = round(float(out["lat"]), 3)
            out["lon"] = round(float(out["lon"]), 3)
    # kws: full precision retained

    if out.get("contains_people"):
        out.pop("image_ref", None)
        out["image_ref"] = "blurred"

    return out


def build_fire_alert_package(raw: Dict[str, Any], audience: str) -> Dict[str, Any]:
    """Fire and bushfire alerts are never released to public or Remote Seat audiences."""
    if audience in ("public", "participant", "guide"):
        return {
            "event": "fire_alert",
            "location": "redacted",
            "level": raw.get("level"),
            "delay_minutes": 9999,
        }
    out = deepcopy(raw)
    out["ranger_only"] = True
    return out


def package_manifest(packages: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"count": len(packages), "species": sorted({p.get("species") for p in packages})}
