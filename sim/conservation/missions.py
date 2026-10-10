"""Mission readiness checks before starting a conservation patrol."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from .apps import ConservationApp, enabled_apps_for_park, profile_for


class ConservationEventType(str, Enum):
    SNARE_SUSPECT = "snare_suspect"
    CARCASS = "carcass"
    FENCE_DAMAGE = "fence_damage"
    HUMAN_INTRUSION = "human_intrusion"
    SPECIES_COUNT = "species_count"
    HWC_ALERT = "hwc_alert"
    FIRE_ALERT = "fire_alert"
    HABITAT_NOTE = "habitat_note"


@dataclass(frozen=True)
class ConservationEvent:
    event_type: ConservationEventType
    lat: float
    lon: float
    payload: Dict[str, Any]
    ranger_only: bool = True


def evaluate_mission_readiness(
    park_id: str,
    app: ConservationApp,
    *,
    path_plan_ref: Optional[str],
    kws_authorization_ref: Optional[str],
    thermal_payload_available: bool,
    wind_ms: float,
    battery_pct: float,
) -> tuple[bool, str]:
    """Gate a Ranger Patrol conservation run. The rover follows a trained path."""
    if app not in enabled_apps_for_park(park_id):
        return False, f"{app.value} not enabled for park {park_id}"

    profile = profile_for(app)
    if profile.kws_only and not kws_authorization_ref:
        return False, "KWS written authorization required"

    if not path_plan_ref:
        return False, "trained path plan required"

    if profile.requires_thermal and not thermal_payload_available:
        return False, "thermal payload required for this mission"

    if wind_ms > 12.0:
        return False, "wind above conservation ops limit"

    if battery_pct < 25.0:
        return False, "battery too low for planned mission"

    return True, "cleared for conservation patrol"
