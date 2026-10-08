"""Stand-off safety envelope for Off-Safari.

Pure functions, no dependencies. The envelope outranks the pilot's route, the
autonomy planner and every remote request. Remote participants never reach this
module with flight commands; they only send camera intents (see
`camera_intent_allowed`).

Default numbers come from published studies, not from local measurement:
responses in most species were triggered below ~60 m above ground level (AGL)
and closer than ~100 m horizontally (Sci Rep, Botswana). Treat them as
starting points and tune them with KWS scientists.

ASSUMPTION: the altitude rule only applies inside `noise_radius_m`. That radius
is our own conservative choice, not a published figure.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

EARTH_RADIUS_M = 6_371_000.0

# Decision severity, lowest to highest. The highest one wins.
OK, CLIMB, RETREAT, ABORT = "OK", "CLIMB", "RETREAT", "ABORT"
_SEVERITY = {OK: 0, CLIMB: 1, RETREAT: 2, ABORT: 3}


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


@dataclass(frozen=True)
class DroneState:
    lat: float
    lon: float
    agl_m: float
    battery_pct: float
    wind_ms: float


@dataclass(frozen=True)
class Animal:
    lat: float
    lon: float
    species: str
    alert: bool = False  # vigilance or agitation detected by vision or the pilot


@dataclass(frozen=True)
class ExclusionZone:
    """Circular no-fly zone, e.g. the rhino sanctuary or a visitor road."""

    name: str
    lat: float
    lon: float
    radius_m: float


@dataclass
class Config:
    min_horizontal_m: float = 100.0
    min_agl_m: float = 60.0
    noise_radius_m: float = 300.0
    alert_multiplier: float = 1.5  # larger stand-off when an animal is alert
    min_battery_pct: float = 30.0
    max_wind_ms: float = 10.0
    # Per-species overrides, e.g. {"nesting_bird": (150.0, 80.0)} as (horizontal, agl).
    species_overrides: Dict[str, Tuple[float, float]] = field(default_factory=dict)

    def limits_for(self, species: str) -> Tuple[float, float]:
        return self.species_overrides.get(species, (self.min_horizontal_m, self.min_agl_m))


@dataclass
class Decision:
    action: str = OK
    reasons: List[str] = field(default_factory=list)

    def escalate(self, action: str, reason: str) -> None:
        self.reasons.append(reason)
        if _SEVERITY[action] > _SEVERITY[self.action]:
            self.action = action


def evaluate(
    drone: DroneState,
    animals: List[Animal],
    zones: List[ExclusionZone],
    config: Optional[Config] = None,
) -> Decision:
    """Return the safest required action for the current state."""
    cfg = config or Config()
    decision = Decision()

    for zone in zones:
        d = haversine_m(drone.lat, drone.lon, zone.lat, zone.lon)
        if d < zone.radius_m:
            decision.escalate(ABORT, "inside exclusion zone '%s'" % zone.name)

    if drone.battery_pct < cfg.min_battery_pct:
        decision.escalate(ABORT, "battery %.0f%% below %.0f%%" % (drone.battery_pct, cfg.min_battery_pct))
    if drone.wind_ms > cfg.max_wind_ms:
        decision.escalate(ABORT, "wind %.1f m/s above %.1f m/s" % (drone.wind_ms, cfg.max_wind_ms))

    for animal in animals:
        h_min, agl_min = cfg.limits_for(animal.species)
        if animal.alert:
            h_min *= cfg.alert_multiplier
            agl_min *= cfg.alert_multiplier
        d = haversine_m(drone.lat, drone.lon, animal.lat, animal.lon)
        if d < h_min:
            decision.escalate(
                RETREAT, "%s at %.0f m, closer than %.0f m%s"
                % (animal.species, d, h_min, " (alert)" if animal.alert else "")
            )
        elif d < cfg.noise_radius_m and drone.agl_m < agl_min:
            decision.escalate(
                CLIMB, "%s within %.0f m and altitude %.0f m below %.0f m"
                % (animal.species, cfg.noise_radius_m, drone.agl_m, agl_min)
            )

    return decision


def camera_intent_allowed(decision: Decision) -> bool:
    """Remote participants may steer the camera only when the envelope is satisfied.

    Camera intents never move the aircraft, so this only gates whether the view
    can change while the pilot or autonomy is correcting a violation.
    """
    return decision.action == OK
