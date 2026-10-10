import copy
import unittest

import patrol_log as plog
import proximity as s

# A point in Nairobi National Park (approximate, for tests only).
LAT, LON = -1.3700, 36.8300


def offset_east(lat, lon, metres):
    """Move roughly `metres` east (good enough for short test distances)."""
    import math
    return lat, lon + metres / (111_320.0 * math.cos(math.radians(lat)))


class ProximityTests(unittest.TestCase):
    def rover(self, **kw):
        base = dict(
            lat=LAT,
            lon=LON,
            speed_mps=1.0,
            on_approved_path=True,
            battery_pct=80.0,
        )
        base.update(kw)
        return s.RoverState(**base)

    def animal(self, metres, species="giraffe", alert=False):
        lat, lon = offset_east(LAT, LON, metres)
        return s.Animal(lat, lon, species, alert)

    def test_clear_when_far_and_slow(self):
        d = s.evaluate(self.rover(), [self.animal(250)], [])
        self.assertEqual(d.action, s.OK)

    def test_retreat_when_too_close(self):
        d = s.evaluate(self.rover(), [self.animal(20)], [])
        self.assertEqual(d.action, s.RETREAT)

    def test_slow_when_near_and_fast(self):
        d = s.evaluate(self.rover(speed_mps=5.0), [self.animal(60)], [])
        self.assertEqual(d.action, s.SLOW)

    def test_alert_animal_widens_viewing_distance(self):
        calm = s.evaluate(self.rover(), [self.animal(50)], [])
        alert = s.evaluate(self.rover(), [self.animal(50, alert=True)], [])
        self.assertEqual(calm.action, s.OK)
        self.assertEqual(alert.action, s.RETREAT)

    def test_species_override(self):
        cfg = s.Config(species_overrides={"nesting_bird": 80.0})
        d = s.evaluate(self.rover(), [self.animal(50, "nesting_bird")], [], cfg)
        self.assertEqual(d.action, s.RETREAT)

    def test_exclusion_zone_aborts(self):
        zone = s.ExclusionZone("rhino sanctuary", LAT, LON, 500.0)
        d = s.evaluate(self.rover(), [], [zone])
        self.assertEqual(d.action, s.ABORT)

    def test_low_battery_and_off_path_abort(self):
        self.assertEqual(s.evaluate(self.rover(battery_pct=10), [], []).action, s.ABORT)
        self.assertEqual(
            s.evaluate(self.rover(on_approved_path=False), [], []).action, s.ABORT
        )

    def test_highest_severity_wins(self):
        zone = s.ExclusionZone("sanctuary", LAT, LON, 500.0)
        d = s.evaluate(self.rover(speed_mps=5.0), [self.animal(20)], [zone])
        self.assertEqual(d.action, s.ABORT)
        self.assertGreaterEqual(len(d.reasons), 2)

    def test_camera_intent_gated_by_envelope(self):
        ok = s.evaluate(self.rover(), [], [])
        bad = s.evaluate(self.rover(), [self.animal(10)], [])
        self.assertTrue(s.camera_intent_allowed(ok))
        self.assertFalse(s.camera_intent_allowed(bad))

    def test_haversine_sanity(self):
        lat, lon = offset_east(LAT, LON, 1000)
        self.assertAlmostEqual(s.haversine_m(LAT, LON, lat, lon), 1000, delta=5)

    def test_corridor_contains_the_road_and_rejects_bush(self):
        path = [
            s.PathPoint(LAT, LON),
            s.PathPoint(*offset_east(LAT, LON, 200)),
        ]
        self.assertTrue(s.inside_corridor(LAT, LON, path, 12.0))
        bush_lat, bush_lon = offset_east(LAT, LON, 0)
        # 40 m north of the road start.
        import math
        bush_lat = LAT + 40.0 / 111_320.0
        self.assertFalse(s.inside_corridor(bush_lat, bush_lon, path, 12.0))
        decision = s.evaluate(self.rover(), [], [], path=path)
        self.assertEqual(decision.action, s.OK)
        off = self.rover(lat=bush_lat, lon=bush_lon)
        self.assertEqual(s.evaluate(off, [], [], path=path).action, s.ABORT)


class PatrolLogTests(unittest.TestCase):
    def build(self):
        log = plog.PatrolLog()
        log.append("2026-10-08T06:00:00Z", {"event": "depart_staging"})
        log.append("2026-10-08T06:05:00Z", {"event": "sighting", "species": "lion"})
        log.append("2026-10-08T06:20:00Z", {"event": "return_staging"})
        return log

    def test_valid_chain_verifies(self):
        self.assertTrue(plog.verify(self.build().entries))

    def test_tampered_payload_detected(self):
        entries = copy.deepcopy(self.build().entries)
        entries[1]["payload"]["species"] = "rhino"
        self.assertFalse(plog.verify(entries))

    def test_removed_entry_detected(self):
        entries = copy.deepcopy(self.build().entries)
        del entries[1]
        self.assertFalse(plog.verify(entries))

    def test_head_changes_with_each_entry(self):
        log = plog.PatrolLog()
        h0 = log.head()
        log.append("t", {"a": 1})
        self.assertNotEqual(h0, log.head())

    def test_flightlog_alias_still_verifies(self):
        import flightlog as fl
        log = fl.FlightLog()
        log.append("t", {"event": "depart"})
        self.assertTrue(fl.verify(log.entries))


if __name__ == "__main__":
    unittest.main()
