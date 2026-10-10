"""Passability grid for the savannah road, planned with the vendored AGV search."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Sequence, Tuple

import numpy as np

from planning.maps.vehicles import Vehicles
from planning.savannah_circuit import (
    CIRCUIT_ID,
    CORNERS,
    PARK_ID,
    SPAWN_XY,
    on_designated_road,
)
from planning.search.astarsearch import astarRoute3D
from planning.search.dijkstrasearch import dijkstraRoute3D
from planning.search.greedysearch import greedyRoute3D

ALGORITHMS = {
    "astar": astarRoute3D,
    "dijkstra": dijkstraRoute3D,
    "greedy": greedyRoute3D,
}

# World extent covering the dirt loop with a margin.
ORIGIN_X = -22.0
ORIGIN_Y = -26.0
CELL_M = 1.0
COLS = 48
ROWS = 46


class PassTile:
    """Minimal tile the AGV search expects (elevation, velocity, isobstacle)."""

    def __init__(self, on_road: bool, velocity_kmh: float):
        self.elevation = 0.0
        self.slope = 0.0
        self.velocity = velocity_kmh if on_road else 0.01
        self._blocked = not on_road

    def isobstacle(self, max_slope: float = 100) -> bool:
        return self._blocked


def cell_center(row: int, col: int) -> Tuple[float, float]:
    return ORIGIN_X + col * CELL_M, ORIGIN_Y + row * CELL_M


def world_to_cell(x: float, y: float) -> Tuple[int, int]:
    col = int(round((x - ORIGIN_X) / CELL_M))
    row = int(round((y - ORIGIN_Y) / CELL_M))
    col = max(0, min(COLS - 1, col))
    row = max(0, min(ROWS - 1, row))
    return row, col


def build_grid() -> np.ndarray:
    moose = Vehicles("MOOSE")
    road_speed = float(moose["max_velocity"]) * 0.75
    grid = np.empty((ROWS, COLS), dtype=object)
    for row in range(ROWS):
        for col in range(COLS):
            x, y = cell_center(row, col)
            grid[row, col] = PassTile(on_designated_road(x, y), road_speed)
    return grid


def _plan_leg(grid, start_xy, goal_xy, algorithm: str) -> List[Tuple[float, float]]:
    route_fn = ALGORITHMS[algorithm]
    start = world_to_cell(*start_xy)
    goal = world_to_cell(*goal_xy)
    route = route_fn(
        grid,
        maxvelocity=float(Vehicles("MOOSE")["max_velocity"]),
        maxslope=float(Vehicles("MOOSE")["max_slope_angle"]),
        start=start,
        goal=goal,
        gridsize=(CELL_M, CELL_M),
    )
    if not route:
        raise RuntimeError(f"No path from {start_xy} to {goal_xy} with {algorithm}")
    # astarRoute3D returns [col, row] pairs.
    return [cell_center(int(item[1]), int(item[0])) for item in route]


def plan_circuit(algorithm: str = "astar") -> List[Tuple[float, float]]:
    """Plan each side of the loop on the road mask and stitch them."""
    if algorithm not in ALGORITHMS:
        raise ValueError(f"algorithm must be one of {sorted(ALGORITHMS)}")
    grid = build_grid()
    stitched: List[Tuple[float, float]] = []
    for start_xy, goal_xy in zip(CORNERS, CORNERS[1:]):
        leg = _plan_leg(grid, start_xy, goal_xy, algorithm)
        if stitched and leg:
            leg = leg[1:]
        stitched.extend(leg)
    if not stitched:
        stitched = [SPAWN_XY]
    return stitched


def waypoints_document(points: Sequence[Tuple[float, float]], algorithm: str) -> dict:
    return {
        "park_id": PARK_ID,
        "circuit_id": CIRCUIT_ID,
        "algorithm": algorithm,
        "loop": False,
        "stop_at_end": True,
        "spawn": {"x": SPAWN_XY[0], "y": SPAWN_XY[1], "z": 0.38},
        "waypoints": [{"x": round(x, 3), "y": round(y, 3), "z": 0.38} for x, y in points],
    }


def write_waypoints(path: Path, algorithm: str = "astar") -> dict:
    document = waypoints_document(plan_circuit(algorithm), algorithm)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return document
