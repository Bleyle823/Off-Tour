import unittest

from conservation import apps, fire, missions
from conservation.apps import ConservationApp
from conservation.fire import FireRiskLevel, ThermalSample


class ConservationMissionTests(unittest.TestCase):
    def test_fire_mission_requires_thermal(self):
        ok, msg = missions.evaluate_mission_readiness(
            "nairobi_national_park",
            ConservationApp.FOREST_FIRE_DETECTION,
            path_plan_ref="circuit-a",
            kws_authorization_ref="kws-auth-001",
            thermal_payload_available=False,
            wind_ms=5.0,
            battery_pct=80.0,
        )
        self.assertFalse(ok)
        self.assertIn("thermal", msg)

    def test_fire_mission_clears_with_thermal(self):
        ok, _ = missions.evaluate_mission_readiness(
            "nairobi_national_park",
            ConservationApp.FOREST_FIRE_DETECTION,
            path_plan_ref="circuit-a",
            kws_authorization_ref="kws-auth-001",
            thermal_payload_available=True,
            wind_ms=5.0,
            battery_pct=80.0,
        )
        self.assertTrue(ok)

    def test_rhino_mission_requires_kws_auth(self):
        ok, msg = missions.evaluate_mission_readiness(
            "nairobi_national_park",
            ConservationApp.RHINO_SURVEILLANCE,
            path_plan_ref="circuit-a",
            kws_authorization_ref=None,
            thermal_payload_available=True,
            wind_ms=5.0,
            battery_pct=80.0,
        )
        self.assertFalse(ok)
        self.assertIn("KWS", msg)

    def test_mission_requires_trained_path(self):
        ok, msg = missions.evaluate_mission_readiness(
            "nairobi_national_park",
            ConservationApp.FOREST_FIRE_DETECTION,
            path_plan_ref=None,
            kws_authorization_ref="kws-auth-001",
            thermal_payload_available=True,
            wind_ms=5.0,
            battery_pct=80.0,
        )
        self.assertFalse(ok)
        self.assertIn("trained path", msg)


class FireDetectionTests(unittest.TestCase):
    def test_no_alert_below_threshold(self):
        samples = [ThermalSample(-1.37, 36.83, 90.0, 0.1)]
        out = fire.assess_fire_from_thermal(samples, wind_ms=3.0, humidity_pct=50.0)
        self.assertEqual(out, [])

    def test_critical_on_high_temp_and_smoke(self):
        samples = [ThermalSample(-1.37, 36.83, 280.0, 0.85)]
        out = fire.assess_fire_from_thermal(samples, wind_ms=5.0, humidity_pct=20.0)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].level, FireRiskLevel.CRITICAL)

    def test_nairobi_has_fire_app_enabled(self):
        enabled = apps.enabled_apps_for_park("nairobi_national_park")
        self.assertIn(ConservationApp.FOREST_FIRE_DETECTION, enabled)


if __name__ == "__main__":
    unittest.main()
