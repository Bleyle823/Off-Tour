"""Path and animal-distance envelope for OFF TOUR.

Pure functions, no dependencies. The envelope outranks the trained-path
autonomy and every remote request. Remote participants never reach this
module with drive commands; they only send camera intents (see
`camera_intent_allowed`).

Default distances are conservative starting points for a ground vehicle on a
designated road. Tune them with KWS scientists. They are not aerial stand-off
figures.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

EARTH_RADIUS_M = 6_371_000.0

# Decision severity, lowest to highest. The highest one wins.
OK, SLOW, RETREAT, ABORT = "OK", "SLOW", "RETREAT", "ABORT"
_SEVERITY = {OK: 0, SLOW: 1, RETREAT: 2, ABORT: 3}


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def _to_local_m(lat: float, lon: float, origin_lat: float, origin_lon: float) -> Tuple[float, float]:
    x = math.radians(lon - origin_lon) * EARTH_RADIUS_M * math.cos(math.radians(origin_lat))
    y = math.radians(lat - origin_lat) * EARTH_RADIUS_M
    return x, y


@dataclass(frozen=True)
class RoverState:
    lat: float
    lon: float
    speed_mps: float
    on_approved_path: bool
    battery_pct: float


@dataclass(frozen=True)
class Animal:
    lat: float
    lon: float
    species: str
    alert: bool = False  # vigilance or agitation detected by vision


@dataclass(frozen=True)
class ExclusionZone:
    """Circular no-entry zone, e.g. the rhino sanctuary."""

    name: str
    lat: float
    lon: float
    radius_m: float


@dataclass(frozen=True)
class PathPoint:
    lat: float
    lon: float


@dataclass
class Config:
    min_viewing_m: float = 40.0
    near_radius_m: float = 80.0
    max_speed_near_wildlife_mps: float = 1.5
    alert_multiplier: float = 1.5  # larger viewing distance when an animal is alert
    min_battery_pct: float = 30.0
    corridor_half_width_m: float = 12.0
    # Per-species viewing distance in metres, e.g. {"nesting_bird": 80.0}.
    species_overrides: Dict[str, float] = field(default_factory=dict)

    def viewing_m_for(self, species: str) -> float:
        return self.species_overrides.get(species, self.min_viewing_m)


@dataclass
class Decision:
    action: str = OK
    reasons: List[str] = field(default_factory=list)

    def escalate(self, action: str, reason: str) -> None:
        self.reasons.append(reason)
        if _SEVERITY[action] > _SEVERITY[self.action]:
            self.action = action


def distance_to_segment_m(lat: float, lon: float, a: PathPoint, b: PathPoint) -> float:
    """Distance from a point to the segment AB, in metres (local tangent plane)."""
    ax, ay = _to_local_m(a.lat, a.lon, lat, lon)
    bx, by = _to_local_m(b.lat, b.lon, lat, lon)
    abx, aby = bx - ax, by - ay
    ab2 = abx * abx + aby * aby
    if ab2 <= 1e-9:
        return math.hypot(ax, ay)
    # Point is the origin in this frame.
    t = max(0.0, min(1.0, (-ax * abx + -ay * aby) / ab2))
    cx, cy = ax + t * abx, ay + t * aby
    return math.hypot(cx, cy)


def distance_to_path_m(lat: float, lon: float, path: Sequence[PathPoint]) -> float:
    if not path:
        return float("inf")
    if len(path) == 1:
        return haversine_m(lat, lon, path[0].lat, path[0].lon)
    return min(
        distance_to_segment_m(lat, lon, path[i], path[i + 1]) for i in range(len(path) - 1)
    )


def inside_corridor(
    lat: float,
    lon: float,
    path: Sequence[PathPoint],
    half_width_m: float,
) -> bool:
    return distance_to_path_m(lat, lon, path) <= half_width_m


def evaluate(
    rover: RoverState,
    animals: List[Animal],
    zones: List[ExclusionZone],
    config: Optional[Config] = None,
    path: Optional[Sequence[PathPoint]] = None,
) -> Decision:
    """Return the safest required action for the current state."""
    cfg = config or Config()
    decision = Decision()

    on_path = rover.on_approved_path
    if path is not None:
        on_path = inside_corridor(rover.lat, rover.lon, path, cfg.corridor_half_width_m)
    if not on_path:
        decision.escalate(ABORT, "left designated self-drive path")

    for zone in zones:
        d = haversine_m(rover.lat, rover.lon, zone.lat, zone.lon)
        if d < zone.radius_m:
            decision.escalate(ABORT, "inside exclusion zone '%s'" % zone.name)

    if rover.battery_pct < cfg.min_battery_pct:
        decision.escalate(ABORT, "battery %.0f%% below %.0f%%" % (rover.battery_pct, cfg.min_battery_pct))

    for animal in animals:
        view_min = cfg.viewing_m_for(animal.species)
        if animal.alert:
            view_min *= cfg.alert_multiplier
        d = haversine_m(rover.lat, rover.lon, animal.lat, animal.lon)
        if d < view_min:
            decision.escalate(
                RETREAT, "%s at %.0f m, closer than %.0f m%s"
                % (animal.species, d, view_min, " (alert)" if animal.alert else "")
            )
        elif d < cfg.near_radius_m and rover.speed_mps > cfg.max_speed_near_wildlife_mps:
            decision.escalate(
                SLOW, "%s within %.0f m at %.1f m/s, above %.1f m/s"
                % (animal.species, cfg.near_radius_m, rover.speed_mps, cfg.max_speed_near_wildlife_mps)
            )

    return decision


def camera_intent_allowed(decision: Decision) -> bool:
    """Remote participants may steer the camera only when the envelope is satisfied.

    Camera intents never move the rover, so this only gates whether the view
    can change while autonomy is correcting a violation.
    """
    return decision.action == OK
