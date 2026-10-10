# Next steps (engineering)

## Done in repo
- Path and proximity envelope, patrol log chain, mock escrow session, camera intents, redaction policy, revenue split demo.
- Conservation mission catalog (incl. forest fire detection), `sim/conservation/`, park config stubs.
- Webots savannah world with a widened designated road, an autonomous Clearpath Moose, and bushfire alerts (`webots/worlds/off_tour_savannah.wbt`).
- AGV search vendored under `planning/`; savannah passability plan writes `config/webots/off_tour_waypoints.json`. The Moose follows that file for one lap (`webots/controllers/moose_safari/path_follow.py`). Local `webots/protos/Moose.proto` (no absolute Webots install path).

## Week 1-2
1. **Regulatory:** email KWS Nairobi National Park warden with the road-based proposal (`templates/kws-intro.md`). Engage Kenyan counsel on filming, data protection, and vehicle use on park roads.
2. **peaq agung:** check whether machine registration is open; register a test machine identity for the rover; wire `session.py` to real ClaimRegistry calls behind a feature flag.
3. **Web client sketch:** remote seat UI (video placeholder, pan/tilt/zoom only, booking status from claim id). No drive controls.
4. **Hardware:** spec the Clearpath Moose reference fit (8×8, closed chassis, mast camera, companion computer, secure element for future Verify). Road-only.

## Week 3-4
5. **Ranger console:** show path-geofence and proximity decisions in real time. The console watches the trained circuit. It does not drive the rover.
6. **Detector:** export ONNX species + person model; run on the companion computer in loop with redaction.
7. **Insurance quote** with the draft operations note from `docs/COMPLIANCE.md`.

## Before any wildlife driving in a park
- Signed KWS permission naming the circuit.
- Independent ecologist signs the disturbance protocol.
- Private-road trials with measured noise and behaviour data.
