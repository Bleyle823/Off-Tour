# OFF TOUR planning

Vendored from the off-road AGV route-planning project (search algorithms and
terrain/vehicle models). The savannah demo does not import the Colorado DEM
or the Webots elevation `.wbo`.

## Run

From the Off-Safari repository root:

```bash
pip install -r requirements.txt
python scripts/planning/run_savannah_plan.py
```

That writes `config/webots/off_tour_waypoints.json`. The Moose controller
`webots/controllers/moose_safari` loads that file and drives one lap, then
stops. `scripts/planning/export_savannah_circuit.py` writes the same file
from the geometric centerline (no search) if you only want an even sample.

```bash
python -m planning.main --algorithm astar
```

Algorithms: `astar` (default), `dijkstra`, `greedy`.

## Nairobi DEM later

`GEngine_Elev` (Google Earth Engine) is how the source AGV project fetched
elevation. It is not wired here. A later step can drop a Nairobi raster into
this planner; the savannah road mask stays the passable corridor until a
warden-approved circuit replaces it.

Figures for the original Colorado tests live in the AGV repo `imgs/` folder.
