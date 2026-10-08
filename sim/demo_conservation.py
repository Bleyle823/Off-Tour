"""Mock Ranger Eye conservation run including bushfire detection.

Run: python -m sim.demo_conservation
"""

from __future__ import annotations

import json

from .conservation import apps, fire, missions
from .conservation.apps import ConservationApp
from .conservation.fire import ThermalSample
from . import flightlog as fl


def main() -> None:
    park = "nairobi_national_park"
    app = ConservationApp.FOREST_FIRE_DETECTION
    ok, msg = missions.evaluate_mission_readiness(
        park,
        app,
        pilot_licensed=True,
        kws_authorization_ref="kws-letter-ref-2026",
        thermal_payload_available=True,
        wind_ms=6.0,
        battery_pct=88.0,
    )
    print("mission readiness:", ok, msg)

    samples = [
        ThermalSample(-1.372, 36.828, 95.0, 0.05),
        ThermalSample(-1.365, 36.835, 210.0, 0.55),
    ]
    alerts = fire.assess_fire_from_thermal(samples, wind_ms=6.0, humidity_pct=28.0)

    log = fl.FlightLog()
    log.append("2026-10-08T14:00:00Z", {"event": "conservation_arm", "app": app.value, "park": park})
    for a in alerts:
        log.append(
            "2026-10-08T14:12:00Z",
            {
                "event": "fire_alert",
                "level": a.level.value,
                "lat": a.lat,
                "lon": a.lon,
                "reason": a.reason,
                "ranger_only": True,
            },
        )

    out = {
        "park": park,
        "profile": apps.profile_for(app).summary,
        "alerts": [a.__dict__ for a in alerts],
        "log_verified": fl.verify(log.entries),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
