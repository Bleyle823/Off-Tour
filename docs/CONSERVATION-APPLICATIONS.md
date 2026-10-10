# Conservation applications (OFF TOUR Ranger Patrol)

Ranger Patrol missions for Kenya national parks and reserves. These run **only** under KWS
supervision, on **designated roads**. The rover follows a trained path by itself. There is no driver aboard. The path geofence and viewing-distance rules outrank that autonomy.
Public **Remote Seat** sessions do not trigger conservation intel feeds.

## Applications

| ID | Mission | Kenya / park relevance | Data class |
| --- | --- | --- | --- |
| C1 | Fence patrol | Vandalism, breaches, electric fence theft (NNP and rhino sites), checked from the road | Ranger only |
| C2 | Snare sweep | Stops along Mbagathi, dispersal, and ranch-edge roads (giraffe, antelope, zebra) | Ranger only |
| C3 | Carcass detection | Poaching and disease early signal visible from the circuit | Ranger only |
| C4 | Thermal dawn/dusk look | Mast or roof thermal sensor at legal stopping points; complements fixed cameras | Ranger only |
| C5 | Wildlife census | Repeatable road transects for KWS population monitoring | KWS / research |
| C6 | Rhino dispersal surveillance | Southern range notes; no public location data; no sanctuary entry | KWS only, max redaction |
| C7 | HWC buffer monitor | Southern NNP lion–livestock interface, from the road | KWS only |
| C8 | Habitat recon | Invasive species, pollution, fragmentation seen from the circuit | KWS / research |
| C9 | **Forest / bushfire detection** | Dry-season grass and bush fires spotted on the patrol route | Ranger only, immediate alert |

## Forest fire detection (C9)

**Purpose:** Detect heat and smoke signatures early so rangers can confirm on the ground and
coordinate with KWS fire response. The rover does not fight fires.

**Signals (onboard):** Thermal brightness temperature from the mast sensor, optional
smoke/heuristic index, wind and humidity context from a weather feed.

**Alert levels:** `watch` → `warning` → `critical` (see `sim/conservation/fire.py`).

**Rules:**

- Fire alerts are **ranger-only**; never on Remote Seat or public streams.
- Coordinates are signed for KWS ops; aggregate fire scars may be shared later for research.
- The patrol stays on the approved road. Minimum viewing distance still applies to wildlife near the fire line. The rover stops; it does not drive into the burn.

## Implementation

- Catalog and profiles: `sim/conservation/apps.py`
- Fire logic: `sim/conservation/fire.py`
- Readiness checks: `sim/conservation/missions.py` (trained path plan, KWS reference)
- Park priorities: `config/parks/`

## Sources (high level)

- Nairobi National Park management plan themes: snaring, HWC, rhino dispersal, habitat loss
  ([Conservation Alliance draft plan](https://www.conservationalliance.or.ke/publications/27-nairobi-national-park-management-plan/file))
- Thermal anti-poaching systems: [WWF Wildlife Crime Technology Project](https://www.worldwildlife.org/our-work/wildlife/wildlife-crime/wildlife-crime-technology-project/)
