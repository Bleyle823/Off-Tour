"""Savannah entry point for OFF TOUR route planning.

The Colorado DEM pipeline stays in the off-road AGV repository. This entry
plans the designated dirt loop in off_tour_savannah.wbt.

Google Earth Engine (GEngine_Elev) is not required for this savannah circuit.
It is the optional later source for a Nairobi National Park elevation raster.
"""

import argparse
from pathlib import Path

from planning.savannah_plan import write_waypoints


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan the OFF TOUR savannah circuit.")
    parser.add_argument(
        "--algorithm",
        choices=("astar", "dijkstra", "greedy"),
        default="astar",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=repo_root() / "config" / "webots" / "off_tour_waypoints.json",
    )
    args = parser.parse_args()
    document = write_waypoints(args.out, args.algorithm)
    print(f"Wrote {len(document['waypoints'])} waypoints to {args.out}")


if __name__ == "__main__":
    main()
