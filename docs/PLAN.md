# OFF TOUR: Project Plan

## 1. Vision and principles

**Vision:** let anyone, anywhere, experience Nairobi National Park through a drone that
behaves like a careful ranger, and turn that attention into money for the park and its
neighbours.

**Principles (these override features):**

1. **Animals first.** If a feature needs the drone closer than the stand-off rule, the feature
   is cut.
2. **A licensed human is always in command.** Autonomy handles routine flight inside a
   geofence. Remote participants control the camera view only, never the flight path.
3. **Regulator-led.** KWS, KCAA and the airport authorities are partners, not obstacles.
   No flights without written approval.
4. **Protect the rhinos.** Location data for sensitive species is never public and never live.
5. **Honest claims.** Say what is live, what is mocked, and what is a plan.

## 2. Users and what they get

| User | Job to be done | What OFF TOUR gives them |
| --- | --- | --- |
| **Remote participant** (diaspora, students, wildlife fans) | See and learn about the park without travelling | A live or near-live session, a "remote seat" to pan and zoom, a guide's commentary, a signed souvenir clip |
| **Schools in Nairobi and Kenya** | Reach a park most pupils never visit | Scheduled classroom sessions at a low or sponsored price |
| **KWS rangers** | Patrol 117 km² with limited staff | Thermal dawn/dusk patrols, fence checks, snare and carcass detection, a verifiable log |
| **Researchers and conservation groups** | Reliable wildlife counts and behaviour data | Signed, timestamped detections with provenance, sold or granted by policy |
| **Tour operators and guides** | Better game finding, extra product | Delayed, non-sensitive sightings; co-branded remote sessions |
| **Community co-owners** | A share of the income from wildlife on their doorstep | Revenue share through a vault, plus local jobs (pilots, technicians, guides) |

## 3. Product: three modes, built in this order

1. **Ranger Eye (license to operate).** Conservation-first flights run or supervised by KWS.
   Earns little directly, but it is what makes the park willing to host the rest. Includes
   thermal patrols, fence and snare patrols, census transects, HWC buffers, and forest /
   bushfire hotspot detection (see `docs/CONSERVATION-APPLICATIONS.md`).
2. **School and Remote Seat sessions (core public product).** Pre-booked 20-30 minute sessions.
   The drone flies an autonomous route along pre-approved corridors at stand-off distance; a
   KCAA-licensed pilot monitors; remote participants steer the camera within a safe envelope
   and can request "look at that giraffe" targets which the autonomy accepts only if safe.
3. **Data and insight products.** Signed sightings and counts for researchers, delayed
   sightings for guides, aggregate dashboards for KWS.

Not in scope for v1: close-up "chase" flights, flying over visitor vehicles, night tourism
flights, any live feed of the rhino sanctuary, selling territory or access rights.

## 4. The hard constraints (from the research)

Details and links in `docs/COMPLIANCE.md` and `docs/SOURCES.md`.

- **Airspace is the biggest risk.** The park is fenced against JKIA and Wilson Airport. Kenyan
  rules require written permission from the aerodrome operator and air navigation provider,
  plus KCAA approval, within 10 km of larger aerodromes and 7 km of smaller ones, and on
  approach and take-off paths. Plan on zones and time windows, and plan for a refusal.
- **Park rules.** Drones are banned without written KWS authorization; KWS lists a daily drone
  charge (KSh 5,000 per drone per day for East African citizens, US$300 for non-residents).
- **Operator rules.** Commercial flights need a KCAA operator certificate, reportedly only for a
  Kenyan-registered company with security clearance, plus per-operation authorization.
  Beyond-visual-line-of-sight flight is case-by-case. Verify the current 2025/2026 rules with
  KCAA or counsel; one source I used is a secondary summary.
- **Wildlife disturbance.** Studies found responses in most species below about 60 m above
  ground and within about 100 m horizontally; giraffe and zebra were among the more sensitive.
  The park is also loud already (aircraft, highway, railway), which may reduce reactions but is
  not proof of harmlessness.
- **Privacy.** Kenyan UAS rules bar imaging people without consent; vehicles carry tourists.
  People must be blurred or excluded at the edge.

## 5. System design (summary)

```
 remote participant (web)       KWS ranger console          researcher / guide
        |  camera intents             |  full access              |  filtered access
        v                             v                           v
   Session service  <--- peaq: booking claim, payments, access grants, ratings --->
        |
        v
   Ground control (human pilot in command, KCAA licensed)
        |  flight plan + approvals       ^ telemetry, video (private link)
        v                                |
   Drone: flight controller + companion computer
        - stand-off safety envelope (hard limits, cannot be overridden remotely)
        - detector (species, people, vehicles) -> blur people, tag animals
        - peaqOS Edge Agent: sign + encrypt + redact -> chunks
        - identity: peaqID + wallet (spend-limited)
```

Key design choices:

- **Two control planes.** Flight control stays local (pilot and onboard autonomy, direct radio
  link). Remote participants only send *camera intents* through a rate-limited service, so
  internet latency or an attacker can never move the aircraft.
- **A safety envelope that outranks everyone.** Minimum horizontal distance and altitude, a
  geofence that excludes the rhino sanctuary and visitor roads, wind and battery limits,
  and a mandatory withdraw when vigilance behaviour is detected. See `sim/standoff.py`.
- **peaq as the trust and settlement layer.** Bookings, payments, signed data, permissions and
  ratings live on peaq; nothing safety-critical waits on a blockchain.

## 6. Hardware options

| Option | Pros | Cons |
| --- | --- | --- |
| Enterprise multirotor with thermal and zoom payload (DJI Matrice class) | Proven, quick to approve, good payloads | Closed software; harder to run onboard signing; supply and type-certificate paperwork |
| Open airframe on PX4 or ArduPilot with a companion computer | Full control of software; runs the ROS 2 Edge Agent and detector natively | More integration work; airworthiness paperwork falls on us |
| Tethered or fixed-wing variants | Tether gives bounded position; fixed-wing covers area quietly | Tether limits reach; fixed-wing has weaker hover for viewing |

Recommendation: start with an enterprise multirotor for Ranger Eye (speed to approval) and run
the open-stack build in parallel for the signing and autonomy work. Pick quieter propellers and
measure sound levels before any wildlife exposure.

## 7. Phases

### Phase 0: simulation and groundwork (weeks 1-8) - no flights
- Software: stand-off envelope, flight-log signing, mock sessions (`sim/`).
- peaq: identity for a simulated drone on the agung testnet, a booking as an Escrow claim, a
  signed detection stream with a redaction policy, a vault payout.
- Legal: engage a Kenyan aviation lawyer; incorporate or partner with a certificated Kenyan
  operator; open talks with KWS, KCAA and Kenya Airports Authority; assemble the risk
  assessment (the KCAA manual requires one for each operation type).
- Welfare: agree a wildlife-disturbance protocol with KWS scientists and an independent
  reviewer.

### Phase 1: private-land pilot (months 3-6)
- Fly the real aircraft on private land or a partner conservancy with livestock or tame
  wildlife, with approvals. WildDrone has trialled beyond-line-of-sight wildlife monitoring in
  Kenya at Ol Pejeta with KCAA, Kenya Air Force air traffic control and local drone firms,
  so there is a path to learn from.
- Measure noise, animal response, link quality, detector accuracy, signing overhead.
- Run the first paid-looking sessions with testnet money and invited participants.

### Phase 2: Nairobi National Park Ranger Eye (months 6-12)
- With written KWS, KCAA and aerodrome approvals, run supervised conservation flights in an
  approved zone and window, away from approach paths and the rhino sanctuary.
- Publish the safety log and the disturbance data. Earn trust before selling anything.

### Phase 3: Remote Seat sessions (months 12-18)
- Limited school sessions, then public bookings in approved windows.
- Switch from testnet to mainnet only after legal sign-off on payments and the vault.

### Phase 4: scale (18 months+)
- More zones and aircraft, other parks (Ol Pejeta, Lake Nakuru, others) with the same
  compliance kit, community co-ownership of additional aircraft.

## 8. Workstreams

| Stream | Owner type | First deliverable |
| --- | --- | --- |
| Regulatory and safety | Aviation counsel + certificated operator | Operations manual and risk assessment per KCAA manual |
| Conservation and welfare | KWS scientists + independent ecologist | Disturbance protocol and stop rules |
| Flight and autonomy | Drone engineers | Stand-off enforcement and geofence on hardware-in-the-loop sim |
| Vision and edge | ML engineer | Detector for animals, people, vehicles; people blur |
| peaq integration | Smart-contract and backend engineers | Identity, Escrow booking, Stream signing, vault |
| Product and community | Product lead + community liaison | School partner pilot, community benefit agreement |

## 9. Money (structure, not numbers)

Revenue lines: school and remote-seat sessions, conservation-data licences, sponsored sessions,
donations. Cost lines: aircraft and spares, insurance, operator and pilot staffing, KWS drone
charges, connectivity, platform costs, welfare monitoring, legal. For comparison, PixCams runs
free, donation-supported wildlife livestreams in Malawi, so assume viewers will not pay much
for passive watching; paid value must come from interaction, schools, data and sponsors.

**Illustrative revenue split for a paid session (design parameter, not a forecast):**
KWS fee and conservation share, operator and pilot costs, community vault, platform and
validators, maintenance and insurance reserve. Set the actual percentages with KWS and the
community before launch.

## 10. Risks

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| Airspace approval refused or limited near JKIA and Wilson | High | Start with the aerodrome operators; design for narrow zones and windows; keep the private-land pilot as fallback |
| Wildlife disturbance or a bad incident | Medium | Conservative stand-off, independent monitoring, kill switch, publish data, stop rules agreed with KWS |
| Poaching risk from location data | Medium | Redaction in the Data Event Map, delays, rhino sanctuary excluded, access grants per buyer |
| Privacy breach (people or vehicles filmed) | Medium | People blur at the edge before signing or streaming; no recording of visitors |
| Payments and vault treated as regulated activity | Medium | Legal review; testnet until cleared; sell sessions before selling ownership |
| Remote control misuse or hacking | Low-Medium | Camera-only control plane, rate limits, signed intents, hard envelope on the aircraft |
| peaq pieces not ready (registration paused, Stream purchase routes 404 today) | Medium | Mock and label; keep the booking and signing logic portable |
| Poor demand for paid remote viewing | Medium | School, sponsor and data revenue first; test willingness to pay in Phase 1 |

## 11. Success measures

- Zero recorded disturbance incidents above the agreed threshold.
- Regulatory approvals secured and published.
- Rangers use the product weekly and say it saves patrol time.
- Remote sessions completed, school hours delivered, repeat bookings.
- Share of revenue reaching the park and community.
- Machine Credit Rating moves from Provisioned toward investment grade on real, signed flight
  history.

## 12. Immediate next steps (next two weeks)

1. Book a call with a Kenyan aviation lawyer and with a certificated RPAS operator.
2. Write to KWS (Nairobi National Park warden) with a one-page proposal and conservation
   offer; do not request filming rights first.
3. Check the current peaq registration status and agung testnet access.
4. Extend `sim/` with the detector interface and the booking and signing flow.
