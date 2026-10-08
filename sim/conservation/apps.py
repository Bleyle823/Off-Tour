"""Conservation application catalog (Kenya national parks focus)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import FrozenSet, Tuple


class ConservationApp(str, Enum):
    """Ranger Eye missions; not available on public Remote Seat sessions."""

    FENCE_PATROL = "fence_patrol"
    SNARE_SWEEP = "snare_sweep"
    CARCASS_DETECTION = "carcass_detection"
    THERMAL_PATROL = "thermal_patrol"
    WILDLIFE_CENSUS = "wildlife_census"
    RHINO_SURVEILLANCE = "rhino_surveillance"
    HWC_BUFFER_MONITOR = "hwc_buffer_monitor"
    HABITAT_RECON = "habitat_recon"
    FOREST_FIRE_DETECTION = "forest_fire_detection"


class DataClass(str, Enum):
    RANGER_ONLY = "ranger_only"
    KWS_RESEARCH = "kws_research"
    DELAYED_PUBLIC = "delayed_public"


@dataclass(frozen=True)
class MissionProfile:
    app: ConservationApp
    summary: str
    data_class: DataClass
    min_agl_m: float = 60.0
    min_standoff_m: float = 100.0
    requires_thermal: bool = False
    kws_only: bool = False


APP_PROFILES: Tuple[MissionProfile, ...] = (
    MissionProfile(
        ConservationApp.FENCE_PATROL,
        "Fence integrity and breach points along park boundaries.",
        DataClass.RANGER_ONLY,
        min_agl_m=50.0,
    ),
    MissionProfile(
        ConservationApp.SNARE_SWEEP,
        "Transect patrols for snares and traps (dispersal edges, river lines).",
        DataClass.RANGER_ONLY,
    ),
    MissionProfile(
        ConservationApp.CARCASS_DETECTION,
        "Early mortality and poaching-indicator surveys.",
        DataClass.RANGER_ONLY,
    ),
    MissionProfile(
        ConservationApp.THERMAL_PATROL,
        "Dawn/dusk thermal patrol complementing fixed cameras.",
        DataClass.RANGER_ONLY,
        requires_thermal=True,
    ),
    MissionProfile(
        ConservationApp.WILDLIFE_CENSUS,
        "Repeatable transects for species counts.",
        DataClass.KWS_RESEARCH,
    ),
    MissionProfile(
        ConservationApp.RHINO_SURVEILLANCE,
        "Dispersal-area rhino monitoring; no public location data.",
        DataClass.RANGER_ONLY,
        kws_only=True,
    ),
    MissionProfile(
        ConservationApp.HWC_BUFFER_MONITOR,
        "Human–wildlife conflict buffer alerts (carnivore presence near settlements).",
        DataClass.RANGER_ONLY,
        kws_only=True,
    ),
    MissionProfile(
        ConservationApp.HABITAT_RECON,
        "Habitat, invasive species, and pollution reconnaissance.",
        DataClass.KWS_RESEARCH,
        min_agl_m=80.0,
    ),
    MissionProfile(
        ConservationApp.FOREST_FIRE_DETECTION,
        "Wildfire and bushfire hotspot detection (thermal + smoke cues).",
        DataClass.RANGER_ONLY,
        requires_thermal=True,
        min_agl_m=70.0,
    ),
)


def profile_for(app: ConservationApp) -> MissionProfile:
    for p in APP_PROFILES:
        if p.app == app:
            return p
    raise KeyError(app)


# Park-specific enablement (see config/parks/).
PARK_ENABLED_APPS: dict[str, FrozenSet[ConservationApp]] = {
    "nairobi_national_park": frozenset(
        {
            ConservationApp.FENCE_PATROL,
            ConservationApp.SNARE_SWEEP,
            ConservationApp.CARCASS_DETECTION,
            ConservationApp.THERMAL_PATROL,
            ConservationApp.WILDLIFE_CENSUS,
            ConservationApp.RHINO_SURVEILLANCE,
            ConservationApp.HWC_BUFFER_MONITOR,
            ConservationApp.HABITAT_RECON,
            ConservationApp.FOREST_FIRE_DETECTION,
        }
    ),
    "generic_kenya_reserve": frozenset(
        {
            ConservationApp.FENCE_PATROL,
            ConservationApp.THERMAL_PATROL,
            ConservationApp.WILDLIFE_CENSUS,
            ConservationApp.HABITAT_RECON,
            ConservationApp.FOREST_FIRE_DETECTION,
        }
    ),
}


def enabled_apps_for_park(park_id: str) -> FrozenSet[ConservationApp]:
    return PARK_ENABLED_APPS.get(park_id, PARK_ENABLED_APPS["generic_kenya_reserve"])
