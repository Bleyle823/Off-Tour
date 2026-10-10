"""End-to-end mock: book -> drive -> log -> validate -> pay -> split.

Run from repo root: python -m sim.demo_session
"""

from __future__ import annotations

import json

from . import camera as cam
from . import patrol_log as fl
from . import proximity as s
from . import redaction as red
from . import session as sess
from . import vault as v

LAT, LON = -1.3700, 36.8300


def main() -> None:
    registry = sess.SessionRegistry()
    claim = registry.create(
        claim_id="claim-001",
        buyer_id="did:peaq:buyer-school-001",
        seller_machine_id="did:peaq:offtour-rover-001",
        price_usdc_cents=2500,
        deadline_iso="2026-10-15T10:00:00Z",
        buyer_stake_cents=100,
    )
    registry.accept("claim-001", seller_stake_cents=100)
    registry.fund("claim-001")

    log = fl.PatrolLog()
    log.append("2026-10-08T06:00:00Z", {"event": "arm", "path_plan": "self-drive-circuit-A"})
    log.append("2026-10-08T06:01:00Z", {"event": "depart", "path": "self-drive-circuit-A"})

    # Rover on an approved circuit; sanctuary is a separate point.
    sanctuary_lat, sanctuary_lon = LAT - 0.008, LON - 0.005
    rover = s.RoverState(
        lat=LAT, lon=LON, speed_mps=1.0, on_approved_path=True, battery_pct=90.0
    )
    animals = [s.Animal(lat=LAT + 0.001, lon=LON + 0.001, species="giraffe")]
    zones = [s.ExclusionZone("rhino_sanctuary", sanctuary_lat, sanctuary_lon, 800.0)]

    camera = cam.CameraController()
    envelope = s.evaluate(rover, animals, zones)
    ok, msg = camera.apply_intent(cam.CameraIntent(pan_delta_deg=10), envelope)
    print("camera intent:", ok, msg, "state:", camera.state)

    raw_sighting = {
        "species": "giraffe",
        "lat": LAT + 0.001,
        "lon": LON + 0.001,
        "contains_people": False,
    }
    for audience in ("participant", "guide", "kws", "public"):
        pkg = red.build_detection_package(raw_sighting, audience)
        log.append(
            "2026-10-08T06:08:00Z",
            {"event": "detection_signed", "audience": audience, "payload": pkg},
        )

    log.append("2026-10-08T06:25:00Z", {"event": "return_staging"})
    assert fl.verify(log.entries)

    validation_ref = "validation://kws/ranger-12/session-2026-10-08"
    registry.complete("claim-001", validation_ref)

    splits = v.split_revenue(claim.price_usdc_cents, v.SplitPolicy())
    out = {
        "claim_status": claim.status.value,
        "patrol_log_head": log.head(),
        "validation": validation_ref,
        "revenue_split_usdc_cents": splits,
        "camera_intents": {"applied": camera.intents_applied, "rejected": camera.intents_rejected},
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
