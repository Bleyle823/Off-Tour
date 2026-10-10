# OFF TOUR: Project Plan

## 1. Vision and principles

**Vision:** let anyone, anywhere, take a telepresent safari on Nairobi National Park's designated tourist self-drive paths, from an autonomous rover that is already trained on that circuit and stays on the road. Guests never drive. There is no driver in the vehicle.

**Principles (these override features):**

1. **Animals first.** If a feature needs the rover closer than the viewing-distance rule, or off the approved path, the feature is cut.
2. **The rover drives the trained circuit by itself.** It is trained on the designated tourist self-drive path. Guests never drive. There is no driver in the vehicle. The path geofence and viewing-distance rules still outrank that autonomy. Written park approval is still required before a real circuit. Remote participants control the camera view only, never steering, throttle, or brakes.
3. **Regulator-led.** Kenya Wildlife Service and park operations set which circuits, speeds, and stopping points are allowed. National Transport and Safety Authority rules apply to the vehicle on public park roads. No session runs without written park approval.
4. **Protect the rhinos.** Location data for sensitive species is never public and never live. The rover does not enter the rhino sanctuary.
5. **Honest claims.** Say what is live, what is mocked, and what is a plan. Aerial drones are not part of this product: they disturb animals and add airspace problems this park does not need.

## 2. Users and what they get

| User | Job to be done | What OFF TOUR gives them |
| --- | --- | --- |
| **Remote participant** (diaspora, students, wildlife fans) | See and learn about the park without travelling | A live or near-live session, a "remote seat" to pan and zoom, a guide's commentary, a signed souvenir clip |
| **Schools in Nairobi and Kenya** | Reach a park most pupils never visit | Scheduled classroom sessions at a low or sponsored price |
| **KWS rangers** | Patrol roads and edges with limited staff | Road patrols with mast sensors: fence checks, snare and carcass cues, a verifiable log |
| **Researchers and conservation groups** | Reliable wildlife counts and behaviour data from the road | Signed, timestamped detections with provenance, sold or granted by policy |
| **Tour operators and guides** | An extra product that does not add vehicles off the road | Delayed, non-sensitive sightings; co-branded remote sessions |
| **Community co-owners** | A share of the income from wildlife on their doorstep | Revenue share through a vault, plus local jobs (technicians and guides) |

## 3. Product: three modes, built in this order

1. **Ranger Patrol (license to operate).** Conservation-first runs on the same designated road network, supervised by KWS. The rover follows the trained circuit by itself. Public guests are not on these sessions. Includes thermal looks from legal stopping points, fence and snare checks along the road, census stops, HWC buffer notes, and dry-season bushfire hotspot detection (see `docs/CONSERVATION-APPLICATIONS.md`).
2. **School and Remote Seat sessions (core public product).** Pre-booked 20-30 minute sessions. The rover follows the trained self-drive circuit at park speed limits. There is no driver aboard. Remote participants steer the camera within a safe envelope and can request "look at that giraffe" only when the proximity rule allows a stop.
3. **Data and insight products.** Signed sightings and counts for researchers, delayed sightings for guides, aggregate dashboards for KWS.

Not in scope for v1: off-road driving, chasing animals, night tourism drives, any live feed of the rhino sanctuary, selling territory or access rights, and any aircraft.

## 4. The hard constraints (from the research)

Details and links in `docs/COMPLIANCE.md` and `docs/SOURCES.md`.

- **Stay on the road.** Nairobi National Park already runs self-drive and guided game drives on a designated road network. OFF TOUR uses that network and does not open new tracks through habitat.
- **Park permission.** Commercial filming, telemetry, and a paid remote product need written KWS authorization. Wildlife must not be baited, chased, or harassed. Equipment can be confiscated on violation.
- **Wildlife disturbance.** A ground vehicle is quieter and more familiar to animals than a multirotor, but closeness, sudden stops, and engine noise still matter. Default viewing distance, a speed cap near herds, and a mandatory withdraw on vigilance are starting rules to tune with KWS scientists.
- **The vehicle is an autonomous road rover, not a guest-driven safari car.** Remote participants never hold a steering wheel. The simulation and reference machine is a Clearpath Moose: 8×8, a closed chassis, and a mast camera, trained on the tourist self-drive circuit.
- **Privacy.** Other visitors' vehicles and people must be blurred or excluded at the edge before signing or streaming.

## 5. System design (summary)

```
 remote participant (web)       KWS ranger console          researcher / guide
        |  camera intents             |  full access              |  filtered access
        v                             v                           v
   Session service  <--- peaq: booking claim, payments, access grants, ratings --->
        |
        v
   Onboard autonomy (trained tourist path; no driver aboard)
        |  path plan + approvals         ^ telemetry, video (private link)
        v                                |
   Rover: drive controller + companion computer
        - designated-path geofence (hard stop if the corridor is left)
        - animal proximity envelope (hard limits, cannot be overridden remotely)
        - detector (species, people, vehicles) -> blur people, tag animals
        - peaqOS Edge Agent: sign + encrypt + redact -> chunks
        - identity: peaqID + wallet (spend-limited)
```

Key design choices:

- **Two control planes.** Drive control stays on the rover (the trained path and onboard speed limits). Remote participants only send *camera intents* through a rate-limited service, so internet latency or an attacker can never move the rover.
- **A safety envelope that outranks everyone.** The rover must stay inside the approved path corridor. Minimum horizontal viewing distance, a speed cap when wildlife is near, exclusion of the rhino sanctuary, battery limits, and a mandatory withdraw when vigilance behaviour is detected. See `sim/proximity.py`.
- **peaq as the trust and settlement layer.** Bookings, payments, signed data, permissions and ratings live on peaq; nothing safety-critical waits on a blockchain.

## 6. Hardware options

| Option | Pros | Cons |
| --- | --- | --- |
| Clearpath Moose (8×8 skid steer, closed chassis, mast camera, GPS and compass) | The simulation and reference vehicle: road-only, drives the trained tourist circuit by itself | Must still meet park vehicle and insurance rules; the circuit has to be wide enough for a vehicle about 3 m long |
| Second identical unit for Ranger Patrol | Separates public sessions from ranger logs | Extra capital and staffing |

Recommendation: the Clearpath Moose is the simulation and reference vehicle (8×8, chassis, mast camera), still road-only. It drives the trained tourist circuit by itself. Add a second unit for patrol only after KWS is using the first. Measure sound at the mast and at the roadside before any wildlife exposure. Do not use multirotors.

## 7. Phases

### Phase 0: simulation and groundwork (weeks 1-8) - no park driving
- Software: path geofence, proximity envelope, patrol log signing, mock sessions (`sim/`).
- Webots: savannah with a widened designated road and a Clearpath Moose (`webots/`).
- peaq: identity for a simulated rover on the agung testnet, a booking as an Escrow claim, a signed detection stream with a redaction policy, a vault payout.
- Legal: engage Kenyan counsel on park commercial use, filming, data protection, and vehicle operation; open talks with KWS park management; draft the disturbance protocol.
- Welfare: agree viewing distance, speed near herds, and stop rules with KWS scientists and an independent reviewer.

### Phase 1: private-road pilot (months 3-6)
- Drive the real rover on a private track or partner conservancy road with livestock or tame wildlife, with the landowner's approval.
- Measure noise, animal response, link quality, detector accuracy, signing overhead, and path-geofence false stops.
- Run the first paid-looking sessions with testnet money and invited participants. The guest still only moves the camera.

### Phase 2: Nairobi National Park Ranger Patrol (months 6-12)
- With written KWS approval, run supervised conservation patrols on an approved circuit, away from the rhino sanctuary.
- Publish the safety log and the disturbance data. Earn trust before selling anything.

### Phase 3: Remote Seat sessions (months 12-18)
- Limited school sessions, then public bookings in approved windows and on approved circuits.
- Switch from testnet to mainnet only after legal sign-off on payments and the vault.

### Phase 4: scale (18 months+)
- More circuits and rovers, other parks (Ol Pejeta, Lake Nakuru, others) with the same road-only kit and community co-ownership of additional machines.

## 8. Workstreams

| Stream | Owner type | First deliverable |
| --- | --- | --- |
| Regulatory and safety | Counsel + park operations liaison | Operations note: circuits, speeds, stops, insurance |
| Conservation and welfare | KWS scientists + independent ecologist | Disturbance protocol and stop rules |
| Drive and autonomy | Robotics engineers | Path geofence and proximity enforcement in simulation |
| Vision and edge | ML engineer | Detector for animals, people, vehicles; people blur |
| peaq integration | Smart-contract and backend engineers | Identity, Escrow booking, Stream signing, vault |
| Product and community | Product lead + community liaison | School partner pilot, community benefit agreement |

## 9. Money (structure, not numbers)

Revenue lines: school and remote-seat sessions, conservation-data licences, sponsored sessions, donations. Cost lines: rover and spares, insurance, technician and guide staffing, park fees for commercial activity, connectivity, platform costs, welfare monitoring, legal. For comparison, PixCams runs free, donation-supported wildlife livestreams in Malawi, so assume viewers will not pay much for passive watching; paid value must come from interaction, schools, data and sponsors.

**Illustrative revenue split for a paid session (design parameter, not a forecast):**
KWS fee and conservation share, operator costs, community vault, platform and validators, maintenance and insurance reserve. Set the actual percentages with KWS and the community before launch.

## 10. Risks

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| Park refuses a telepresent product on self-drive roads | Medium | Start with Ranger Patrol and a written welfare protocol; keep the private-road pilot as fallback |
| Wildlife disturbance from stops and engine noise | Medium | Conservative viewing distance, speed cap, independent monitoring, publish data, stop rules agreed with KWS |
| Rover leaves the designated path | Low-Medium | Hard geofence and automatic stop. Autonomy may only resume on the trained path |
| Poaching risk from location data | Medium | Redaction in the Data Event Map, delays, rhino sanctuary excluded, access grants per buyer |
| Privacy breach (people or vehicles filmed) | Medium | People blur at the edge before signing or streaming; no recording of visitors |
| Payments and vault treated as regulated activity | Medium | Legal review; testnet until cleared; sell sessions before selling ownership |
| Remote control misuse or hacking | Low-Medium | Camera-only control plane, rate limits, signed intents, hard envelope on the rover |
| peaq pieces not ready (registration paused, Stream purchase routes 404 today) | Medium | Mock and label; keep the booking and signing logic portable |
| Poor demand for paid remote viewing | Medium | School, sponsor and data revenue first; test willingness to pay in Phase 1 |

## 11. Success measures

- Zero recorded disturbance incidents above the agreed threshold.
- Written park approval for the first circuit, published with the operating rules.
- Rangers use road patrol weekly and say it saves time on fence and fire checks.
- Remote sessions completed, school hours delivered, repeat bookings.
- Share of revenue reaching the park and community.
- Machine Credit Rating moves from Provisioned toward investment grade on real, signed patrol history.

## 12. Immediate next steps (next two weeks)

1. Write to KWS (Nairobi National Park warden) with a one-page proposal: road-based telepresent sessions and ranger patrol, no aircraft.
2. Engage Kenyan counsel on commercial filming, data protection, and operating a small vehicle on park roads.
3. Check the current peaq registration status and agung testnet access.
4. Keep `sim/proximity.py` and the Webots road loop as the safety reference.
