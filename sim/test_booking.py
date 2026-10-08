import unittest

import camera as cam
import redaction as red
import session as sess
import standoff as s
import vault as v


class SessionTests(unittest.TestCase):
    def test_happy_path(self):
        r = sess.SessionRegistry()
        r.create("c1", "b1", "m1", 1000, "2026-01-01T00:00:00Z", 50)
        r.accept("c1", 50)
        r.fund("c1")
        c = r.complete("c1", "val-1")
        self.assertEqual(c.status, sess.ClaimStatus.COMPLETED)

    def test_fund_before_accept_fails(self):
        r = sess.SessionRegistry()
        r.create("c1", "b1", "m1", 1000, "2026-01-01T00:00:00Z", 50)
        with self.assertRaises(ValueError):
            r.fund("c1")


class RedactionTests(unittest.TestCase):
    def test_fire_alert_redacted_for_public(self):
        raw = {"event": "fire_alert", "level": "warning", "lat": -1.0, "lon": 36.0}
        pub = red.build_fire_alert_package(raw, "public")
        self.assertEqual(pub["location"], "redacted")
        self.assertNotIn("lat", pub)

    def test_rhino_coords_stripped_for_public(self):
        raw = {"species": "black_rhino", "lat": -1.0, "lon": 36.0}
        pub = red.build_detection_package(raw, "public")
        self.assertEqual(pub["location"], "redacted")
        self.assertNotIn("lat", pub)

    def test_people_blurred(self):
        raw = {"species": "lion", "lat": -1.0, "lon": 36.0, "contains_people": True, "image_ref": "x"}
        out = red.build_detection_package(raw, "participant")
        self.assertEqual(out["image_ref"], "blurred")


class VaultTests(unittest.TestCase):
    def test_split_sums(self):
        parts = v.split_revenue(10000, v.SplitPolicy())
        self.assertEqual(sum(parts.values()), 10000)


class CameraEnvelopeTests(unittest.TestCase):
    def test_reject_when_retreat(self):
        ctrl = cam.CameraController()
        drone = s.DroneState(-1.37, 36.83, 80, 90, 3)
        animal = s.Animal(-1.37, 36.8305, "giraffe")
        decision = s.evaluate(drone, [animal], [])
        ok, _ = ctrl.apply_intent(cam.CameraIntent(pan_delta_deg=5), decision)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
