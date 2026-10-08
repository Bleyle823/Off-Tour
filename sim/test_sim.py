import copy
import unittest

import standoff as s
import flightlog as fl

# A point in Nairobi National Park (approximate, for tests only).
LAT, LON = -1.3700, 36.8300


def offset_east(lat, lon, metres):
    """Move roughly `metres` east (good enough for short test distances)."""
    import math
    return lat, lon + metres / (111_320.0 * math.cos(math.radians(lat)))


class StandoffTests(unittest.TestCase):
    def drone(self, **kw):
        base = dict(lat=LAT, lon=LON, agl_m=80.0, battery_pct=80.0, wind_ms=3.0)
        base.update(kw)
        return s.DroneState(**base)

    def animal(self, metres, species="giraffe", alert=False):
        lat, lon = offset_east(LAT, LON, metres)
        return s.Animal(lat, lon, species, alert)

    def test_clear_when_far_and_high(self):
        d = s.evaluate(self.drone(), [self.animal(250)], [])
        self.assertEqual(d.action, s.OK)

    def test_retreat_when_too_close(self):
        d = s.evaluate(self.drone(), [self.animal(60)], [])
        self.assertEqual(d.action, s.RETREAT)

    def test_climb_when_in_noise_radius_and_low(self):
        d = s.evaluate(self.drone(agl_m=40.0), [self.animal(200)], [])
        self.assertEqual(d.action, s.CLIMB)

    def test_alert_animal_widens_standoff(self):
        calm = s.evaluate(self.drone(), [self.animal(120)], [])
        alert = s.evaluate(self.drone(), [self.animal(120, alert=True)], [])
        self.assertEqual(calm.action, s.OK)
        self.assertEqual(alert.action, s.RETREAT)

    def test_species_override(self):
        cfg = s.Config(species_overrides={"nesting_bird": (150.0, 80.0)})
        d = s.evaluate(self.drone(), [self.animal(120, "nesting_bird")], [], cfg)
        self.assertEqual(d.action, s.RETREAT)

    def test_exclusion_zone_aborts(self):
        zone = s.ExclusionZone("rhino sanctuary", LAT, LON, 500.0)
        d = s.evaluate(self.drone(), [], [zone])
        self.assertEqual(d.action, s.ABORT)

    def test_low_battery_and_wind_abort(self):
        self.assertEqual(s.evaluate(self.drone(battery_pct=10), [], []).action, s.ABORT)
        self.assertEqual(s.evaluate(self.drone(wind_ms=15), [], []).action, s.ABORT)

    def test_highest_severity_wins(self):
        zone = s.ExclusionZone("road", LAT, LON, 500.0)
        d = s.evaluate(self.drone(agl_m=40.0), [self.animal(60)], [zone])
        self.assertEqual(d.action, s.ABORT)
        self.assertGreaterEqual(len(d.reasons), 2)

    def test_camera_intent_gated_by_envelope(self):
        ok = s.evaluate(self.drone(), [], [])
        bad = s.evaluate(self.drone(), [self.animal(50)], [])
        self.assertTrue(s.camera_intent_allowed(ok))
        self.assertFalse(s.camera_intent_allowed(bad))

    def test_haversine_sanity(self):
        lat, lon = offset_east(LAT, LON, 1000)
        self.assertAlmostEqual(s.haversine_m(LAT, LON, lat, lon), 1000, delta=5)


class FlightLogTests(unittest.TestCase):
    def build(self):
        log = fl.FlightLog()
        log.append("2026-10-08T06:00:00Z", {"event": "takeoff"})
        log.append("2026-10-08T06:05:00Z", {"event": "sighting", "species": "lion"})
        log.append("2026-10-08T06:20:00Z", {"event": "landing"})
        return log

    def test_valid_chain_verifies(self):
        self.assertTrue(fl.verify(self.build().entries))

    def test_tampered_payload_detected(self):
        entries = copy.deepcopy(self.build().entries)
        entries[1]["payload"]["species"] = "rhino"
        self.assertFalse(fl.verify(entries))

    def test_removed_entry_detected(self):
        entries = copy.deepcopy(self.build().entries)
        del entries[1]
        self.assertFalse(fl.verify(entries))

    def test_head_changes_with_each_entry(self):
        log = fl.FlightLog()
        h0 = log.head()
        log.append("t", {"a": 1})
        self.assertNotEqual(h0, log.head())


if __name__ == "__main__":
    unittest.main()
