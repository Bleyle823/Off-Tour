# Conservation applications (OFF TOUR Ranger Eye)

Ranger Eye missions for Kenya national parks and reserves. These run **only** under KWS
supervision with a licensed pilot in command. Public **Remote Seat** sessions do not trigger
conservation intel feeds.

## Applications

| ID | Mission | Kenya / park relevance | Data class |
| --- | --- | --- | --- |
| C1 | Fence patrol | Vandalism, breaches, electric fence theft (NNP and rhino sites) | Ranger only |
| C2 | Snare sweep | Mbagathi, dispersal, ranch edges (giraffe, antelope, zebra) | Ranger only |
| C3 | Carcass detection | Poaching and disease early signal | Ranger only |
| C4 | Thermal dawn/dusk patrol | Complements fixed FLIR; mobile gaps | Ranger only |
| C5 | Wildlife census | KWS population monitoring transects | KWS / research |
| C6 | Rhino dispersal surveillance | Southern range beyond carrying capacity | KWS only, max redaction |
| C7 | HWC buffer monitor | Southern NNP lion–livestock interface | KWS only |
| C8 | Habitat recon | Invasive species, pollution, fragmentation | KWS / research |
| C9 | **Forest / bushfire detection** | Dry-season grass and bush fires in parks and buffer land | Ranger only, immediate alert |

## Forest fire detection (C9)

**Purpose:** Detect heat and smoke signatures early so rangers can confirm on the ground and
coordinate with KWS fire response (not autonomous firefighting from the aircraft).

**Signals (onboard):** Thermal brightness temperature, optional smoke/heuristic index, wind and
humidity context from ground weather feed.

**Alert levels:** `watch` → `warning` → `critical` (see `sim/conservation/fire.py`).

**Rules:**

- Fire alerts are **ranger-only**; never on Remote Seat or public streams.
- Coordinates are signed for KWS ops; aggregate fire scars may be shared later for research.
- Flight stays in approved corridors; stand-off rules still apply to wildlife near fire lines.

## Implementation

- Catalog and profiles: `sim/conservation/apps.py`
- Fire logic: `sim/conservation/fire.py`
- Arm checks: `sim/conservation/missions.py`
- Park priorities: `config/parks/`

## Sources (high level)

- Nairobi National Park management plan themes: snaring, HWC, rhino dispersal, habitat loss
  ([Conservation Alliance draft plan](https://www.conservationalliance.or.ke/publications/27-nairobi-national-park-management-plan/file))
- KWS technology direction: drones for conservation, counting, anti-poaching, HWC (public KWS
  strategy summaries)
- Thermal anti-poaching systems: [WWF Wildlife Crime Technology Project](https://www.worldwildlife.org/our-work/wildlife/wildlife-crime/wildlife-crime-technology-project/)
