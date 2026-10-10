# OFF TOUR

**Tele-present park tours from the road.** An autonomous Clearpath Moose, trained on Nairobi National Park's designated tourist self-drive paths, drives that circuit by itself. There is no driver aboard. People anywhere take a "remote seat" to look around, learn and pay. They steer the camera, never the vehicle. Sightings are signed at the source, bookings are escrowed, the safety record builds a public credit rating, and income is shared with the park and the community, all on [peaq](https://www.peaq.xyz).

> Status: plan and first prototype. Nothing here has park approval yet. Read
> `docs/COMPLIANCE.md` before anyone drives in a protected area.

## The one-paragraph idea

Nairobi National Park is the world's only national park inside a capital city: 117 km², about
460,000 visitors in 2025, black and white rhino, lion, leopard, giraffe, buffalo, no
resident elephants. Most people who love wildlife will never visit it. Visitors already
use a network of self-drive and game-drive roads. **OFF TOUR** puts an autonomous
Clearpath Moose on those roads. It is already trained on the tourist self-drive circuit,
drives that path by itself, and stops at a respectful distance. There is no driver in the
vehicle. Remote participants steer the *camera* (never the wheels). The same machine can run a
conservation patrol for rangers: fence-line checks from the road, snare and carcass cues,
and **forest / bushfire hotspot alerts** in dry season. The path geofence and the
viewing-distance rules outrank the autonomy. peaq gives the rover a verifiable identity, a
wallet, escrowed bookings, signed data, and a credit record.

Aerial drones are not part of this product. They disturb animals and collide with the
airspace around this park. The rover stays on the ground, on the path.

## Ranger Patrol conservation

KWS-supervised missions on the designated road network (not public Remote Seat): fence
patrol, snare sweep, carcass detection, census stops, rhino dispersal notes, HWC buffer
monitoring, habitat recon, and **forest fire detection**. Catalog:
`docs/CONSERVATION-APPLICATIONS.md`. Code: `sim/conservation/`, park profiles in
`config/parks/`.

## Why peaq (and what each piece does here)

| Need | peaq piece | Notes |
| --- | --- | --- |
| The rover is an accountable economic actor | peaqOS Activate: peaqID, wallet, Machine NFT | Registration was marked paused in the docs when researched. Check first. |
| Booking and paying for a session | peaq Escrow (ERC-8004, ClaimRegistry, BaseEscrow, LayerZero) | Buyer funds on Base, claim state lives on peaq |
| Footage and detections nobody can fake | peaqOS Stream: Edge Agent signs and encrypts at capture (ROS 2) | Field rules redact protected species locations |
| Rover buys power, compute, connectivity | peaqOS Scale (agent pairing, spend limits, x402) | Charging revenue splits across co-owners |
| Permits and safety as checkable facts | ERC-8004 Validation and Reputation registries | KWS authorizations recorded as attestations |
| A safety and reliability record | peaqOS Qualify (Machine Credit Rating) | Needed for insurance and financing |
| Community co-ownership | Own vault contract (peaq's Tokenize is not shipped) | Same pattern as the sibling `moonad` project |

Detail in `docs/PEAQ-INTEGRATION.md`.

## Repo map

- `docs/PLAN.md` - the project plan: users, product, phases, workstreams, milestones, risks
- `docs/CONSERVATION-APPLICATIONS.md` - Ranger Patrol missions including bushfire detection
- `docs/COMPLIANCE.md` - park, vehicle, privacy and wildlife checklists, with sources
- `docs/PEAQ-INTEGRATION.md` - architecture, booking flow, data policy, what is live vs mocked
- `docs/SOURCES.md` - every external fact used, with links and dates
- `docs/NEXT-STEPS.md` - engineering and regulatory queue
- `templates/kws-intro.md` - draft letter to KWS (edit before sending)
- `config/parks/` - park conservation priorities and path notes
- `planning/` - AGV search (A*, Dijkstra, greedy) and a savannah road planner. See `planning/README.md`.
- `config/webots/off_tour_waypoints.json` - one lap of the designated dirt loop for the Moose.
- `webots/` - Webots R2025a savannah (open `webots/worlds/off_tour_savannah.wbt`):
  - Dry prickly ground texture plus ~70% wind-sway tall grass (`tallGrassCover`, `grass_wind`)
  - Scaled sassafras trees (forest_firefighters style)
  - Grazing herd: `herd` supervisor drives paths and hinge leg motors on `GrazingWalker` Robots
  - ~70% tall grass via `TallGrassLayer` (single batched PROTO; `maxGrassTufts` caps load time)
  - A widened designated dirt-road loop and a Clearpath Moose (8×8, closed chassis, mast camera); `moose_safari` follows the trained centerline, stops on the path to aim the camera, zoom with `+`/`-` or Page Up/Down, pan with Left/Right, tilt with Up/Down
  - Bushfires on both sides; ranger-only fire alerts in `controllers/moose_safari`
- `sim/` - product logic prototype (pure Python, no dependencies):
  - `proximity.py` - path and animal-distance envelope (outranks autonomy and remote users)
  - `patrol_log.py` - hash-chained patrol log (placeholder for Stream signing); `flightlog.py` re-exports it
  - `session.py` - mock peaq Escrow claim lifecycle
  - `camera.py` - remote camera intents only
  - `redaction.py` - Stream-style field rules (rhino coords, people blur, fire alerts)
  - `vault.py` - revenue split after a completed session
  - `conservation/` - mission catalog, readiness checks, fire detection
  - `demo_session.py` - end-to-end Remote Seat mock run
  - `demo_conservation.py` - Ranger Patrol fire-detection mock run

```bash
cd C:\Users\Omen\Desktop\Off-Safari-main
pip install -r requirements.txt
python scripts/planning/run_savannah_plan.py
python -m unittest discover -s sim -v
python -m unittest planning.tests.test_savannah -v
python -m sim.demo_session
python -m sim.demo_conservation
```

Then open `webots/worlds/off_tour_savannah.wbt` in Webots R2025a and press Play.
The Moose loads `config/webots/off_tour_waypoints.json` and drives one lap of the dirt road.
