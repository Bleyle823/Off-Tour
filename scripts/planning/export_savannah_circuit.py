"""Write an evenly sampled centerline (no search) for the savannah loop."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from planning.savannah_circuit import CIRCUIT_ID, PARK_ID, SPAWN_XY, densify  # noqa: E402
from planning.savannah_plan import waypoints_document  # noqa: E402


def main() -> None:
    out = ROOT / "config" / "webots" / "off_tour_waypoints.json"
    points = densify(spacing_m=2.0)
    document = waypoints_document(points, algorithm="centerline")
    document["park_id"] = PARK_ID
    document["circuit_id"] = CIRCUIT_ID
    document["spawn"] = {"x": SPAWN_XY[0], "y": SPAWN_XY[1], "z": 0.38}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(document['waypoints'])} centerline waypoints to {out}")


if __name__ == "__main__":
    main()
