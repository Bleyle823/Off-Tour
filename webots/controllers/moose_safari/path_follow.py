"""Waypoint pursuit for the OFF TOUR Moose.

Pure functions: no Webots import, so unit tests can run outside the simulator.
Steering matches the savannah dirt loop: spin in place through a sharp corner,
then drive. The follower stops at the last waypoint (one lap, no wrap).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

Point = Tuple[float, float]

DISTANCE_TOLERANCE = 4.0
PIVOT = 0.55
CRUISE = 2.4
SPIN = 10.0
MAX_WHEEL = 8.0


def clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def wrap_angle(angle: float) -> float:
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle


def wheel_speeds(forward: float, turn: float) -> Tuple[float, float]:
    left = clamp(forward - turn, -MAX_WHEEL, MAX_WHEEL)
    right = clamp(forward + turn, -MAX_WHEEL, MAX_WHEEL)
    return left, right


def pursuit_command(
    x: float,
    y: float,
    robot_angle: float,
    target: Point,
    blocked: bool = False,
) -> Tuple[float, float]:
    """Left and right wheel speeds toward one target. Pivot when the heading is wide."""
    dx = target[0] - x
    dy = target[1] - y
    distance = math.hypot(dx, dy)
    if distance < 1e-6:
        return 0.0, 0.0
    target_angle = math.atan2(dy / distance, dx / distance)
    error = wrap_angle(target_angle - robot_angle)
    if abs(error) > PIVOT:
        forward = 0.0
        turn = math.copysign(SPIN, error)
    else:
        forward = CRUISE * (1.0 - abs(error) / PIVOT)
        turn = clamp(6.0 * error, -MAX_WHEEL, MAX_WHEEL)
    if blocked and abs(error) <= PIVOT:
        forward = 0.0
        turn = 0.0
    return wheel_speeds(forward, turn)


# Used when config/webots/off_tour_waypoints.json is missing.
FALLBACK_WAYPOINTS: List[Point] = [
    (17.6, 9.6),
    (17.6, -17.6),
    (-12.0, -17.6),
    (-12.0, 9.6),
]


def find_waypoints_file(start: Path) -> Optional[Path]:
    for parent in [start, *start.parents]:
        candidate = parent / "config" / "webots" / "off_tour_waypoints.json"
        if candidate.is_file():
            return candidate
    return None


def load_waypoints(start: Path) -> Tuple[List[Point], bool]:
    path = find_waypoints_file(start)
    if path is None:
        return list(FALLBACK_WAYPOINTS), True
    document = json.loads(path.read_text(encoding="utf-8"))
    points = [(float(item["x"]), float(item["y"])) for item in document["waypoints"]]
    if len(points) < 1:
        return list(FALLBACK_WAYPOINTS), True
    return points, bool(document.get("stop_at_end", True))


class WaypointFollower:
    def __init__(self, waypoints: Sequence[Point], stop_at_end: bool = True):
        if len(waypoints) < 1:
            raise ValueError("waypoints must not be empty")
        self.waypoints: List[Point] = [(float(x), float(y)) for x, y in waypoints]
        self.index = 0
        self.stop_at_end = stop_at_end
        self.finished = False

    def command(
        self, x: float, y: float, robot_angle: float, blocked: bool = False
    ) -> Tuple[float, float, Optional[Point]]:
        """Return left speed, right speed, and the new target if the index advanced."""
        if self.finished:
            return 0.0, 0.0, None
        advanced: Optional[Point] = None
        # Dense A* samples are about 1 m apart. Skip every sample already
        # inside the arrival bubble so the target stays ahead of the rover.
        while True:
            target = self.waypoints[self.index]
            distance = math.hypot(target[0] - x, target[1] - y)
            if distance >= DISTANCE_TOLERANCE:
                break
            if self.index + 1 >= len(self.waypoints):
                if self.stop_at_end:
                    self.finished = True
                    return 0.0, 0.0, advanced
                self.index = 0
                advanced = self.waypoints[0]
                break
            self.index += 1
            advanced = self.waypoints[self.index]
        left, right = pursuit_command(x, y, robot_angle, target, blocked=blocked)
        return left, right, advanced
