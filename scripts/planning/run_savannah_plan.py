"""Plan the savannah road with A* (or Dijkstra / greedy) and write waypoints."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from planning.savannah_plan import write_waypoints  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--algorithm", choices=("astar", "dijkstra", "greedy"), default="astar")
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "config" / "webots" / "off_tour_waypoints.json",
    )
    args = parser.parse_args()
    document = write_waypoints(args.out, args.algorithm)
    count = len(document["waypoints"])
    if count < 4:
        raise SystemExit(f"expected at least 4 waypoints, got {count}")
    print(f"Wrote {count} waypoints ({args.algorithm}) to {args.out}")


if __name__ == "__main__":
    main()
