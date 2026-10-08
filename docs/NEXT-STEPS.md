# Next steps (engineering)

## Done in repo
- Stand-off envelope, flight log chain, mock escrow session, camera intents, redaction policy, revenue split demo.
- Conservation mission catalog (incl. forest fire detection), `sim/conservation/`, park config stubs.
- Webots savannah world with two Mavic patrol drones and bushfire alerts (`webots/worlds/off_tour_savannah.wbt`).

## Week 1-2
1. **Regulatory:** retain Kenyan aviation counsel; email KWS Nairobi National Park warden with Ranger Eye proposal (template in `templates/kws-intro.md` when added).
2. **peaq agung:** check whether machine registration is open; register a test machine identity; wire `session.py` to real ClaimRegistry calls behind a feature flag.
3. **Web client sketch:** remote seat UI (video placeholder, pan/tilt/zoom only, booking status from claim id).
4. **Hardware:** choose airframe (Matrice vs PX4); spec secure element for future Verify.

## Week 3-4
5. **Ground station:** pilot console showing envelope decisions in real time.
6. **Detector:** export ONNX species + person model; run on companion computer in loop with redaction.
7. **Insurance quote** with draft operations manual from `docs/COMPLIANCE.md`.

## Before any wildlife flight
- Signed KWS + KCAA + aerodrome permissions.
- Independent ecologist signs disturbance protocol.
- Private-land or conservancy trials with measured noise and behaviour data.
