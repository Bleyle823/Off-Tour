"""Designated dirt-road loop in webots/worlds/off_tour_savannah.wbt.

Road boxes (translation, size x y):
  (2.8, 9.6)  38.4 x 8.8   north
  (2.8, -17.6) 38.4 x 8.8  south
  (-12, -4)   8.8 x 36     west
  (17.6, -4)  8.8 x 36     east

The rover spawn is the west end of the north road: (-12, 9.6).
"""

from __future__ import annotations

import math
from typing import List, Sequence, Tuple

Point = Tuple[float, float]

# Closed centerline, matching the corners moose_safari used to hard-code.
CORNERS: List[Point] = [
    (-12.0, 9.6),
    (17.6, 9.6),
    (17.6, -17.6),
    (-12.0, -17.6),
    (-12.0, 9.6),
]

ROAD_HALF_WIDTH_M = 4.0
CIRCUIT_ID = "self_drive_circuit_a"
PARK_ID = "nairobi_national_park"
SPAWN_XY = CORNERS[0]


def _dist_point_segment(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    abx, aby = bx - ax, by - ay
    length_sq = abx * abx + aby * aby
    if length_sq <= 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * abx + (py - ay) * aby) / length_sq))
    return math.hypot(px - (ax + t * abx), py - (ay + t * aby))


def on_designated_road(x: float, y: float, half_width: float = ROAD_HALF_WIDTH_M) -> bool:
    """True when (x, y) is inside the road corridor around the centerline."""
    for (ax, ay), (bx, by) in zip(CORNERS, CORNERS[1:]):
        if _dist_point_segment(x, y, ax, ay, bx, by) <= half_width:
            return True
    return False


def densify(corners: Sequence[Point] = None, spacing_m: float = 2.0) -> List[Point]:
    """Evenly sample the closed centerline. Includes the closing return to spawn."""
    corners = list(corners or CORNERS)
    points: List[Point] = []
    for (ax, ay), (bx, by) in zip(corners, corners[1:]):
        length = math.hypot(bx - ax, by - ay)
        steps = max(1, int(math.ceil(length / spacing_m)))
        for step in range(steps):
            t = step / steps
            points.append((ax + t * (bx - ax), ay + t * (by - ay)))
    points.append(corners[-1])
    return points
