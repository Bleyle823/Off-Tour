"""Planner export and waypoint pursuit, without Webots."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTROLLER = ROOT / "webots" / "controllers" / "moose_safari"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CONTROLLER))

from path_follow import WaypointFollower, load_waypoints, pursuit_command  # noqa: E402
from planning.savannah_circuit import on_designated_road  # noqa: E402
from planning.savannah_plan import plan_circuit, waypoints_document  # noqa: E402


class SavannahPlanTests(unittest.TestCase):
    def test_road_mask_covers_spawn(self):
        self.assertTrue(on_designated_road(-12.0, 9.6))
        self.assertFalse(on_designated_road(0.0, 0.0))

    def test_plan_has_a_full_lap(self):
        points = plan_circuit("astar")
        self.assertGreaterEqual(len(points), 4)
        document = waypoints_document(points, "astar")
        self.assertEqual(document["circuit_id"], "self_drive_circuit_a")
        self.assertTrue(document["stop_at_end"])
        self.assertGreaterEqual(len(document["waypoints"]), 4)

    def test_saved_waypoints_file(self):
        path = ROOT / "config" / "webots" / "off_tour_waypoints.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(document["waypoints"]), 4)
        points, stop = load_waypoints(CONTROLLER)
        self.assertTrue(stop)
        self.assertEqual(len(points), len(document["waypoints"]))


class PathFollowTests(unittest.TestCase):
    def test_pursuit_drives_toward_target(self):
        left, right = pursuit_command(0.0, 0.0, 0.0, (10.0, 0.0))
        self.assertGreater(left, 0.0)
        self.assertGreater(right, 0.0)

    def test_stops_at_last_waypoint(self):
        follower = WaypointFollower([(0.0, 0.0), (1.0, 0.0)], stop_at_end=True)
        left, right, _advanced = follower.command(1.0, 0.0, 0.0)
        self.assertTrue(follower.finished)
        self.assertEqual((left, right), (0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
