# Compliance checklist

> Not legal advice. Rules change. Confirm every item with KWS, park management, and Kenyan
> counsel before any vehicle operates in a protected area or any commercial filming starts.

OFF TOUR is a **ground** product: an autonomous Clearpath Moose on designated tourist
self-drive paths. It is trained on that circuit and drives it by itself. There is no driver
aboard. It does not fly. Aerial unmanned aircraft are not the operating plan.

## A. Park access and vehicle operation (KWS)

| Item | What we know | Our action |
| --- | --- | --- |
| Written authorization | Commercial activity, filming, and research equipment in a national park need KWS permission. Nairobi National Park rules prohibit disturbing wildlife. | Do not enter the park until a written approval names the circuit, hours, and vehicle. |
| Stay on designated roads | The park already has self-drive and guided game-drive roads. Off-road driving damages habitat and is not part of this product. | Hard path geofence in software. If the corridor is left, the rover stops and may only resume on the trained path. No bush driving. |
| Wildlife welfare | No baiting, chasing, or harassment. Equipment can be confiscated on violation. | Viewing-distance and speed rules in `sim/proximity.py`, agreed with KWS scientists before live use. |
| Fees | Park entry and commercial filming fees apply. Confirm the current schedule with KWS; do not assume a drone-day tariff. | Budget park and filming fees as a cost line, not an aviation charge. |
| Vehicle on park roads | The reference vehicle drives the trained tourist circuit by itself. Insurance, a machine that can stop and yield, and written park approval are still required. Counsel and KWS have to confirm that an uncrewed vehicle is permitted on that road. | No driver rides in the vehicle. Remote guests never steer. Path and viewing-distance rules outrank the autonomy. |
| Insurance | Operators of commercial activity are expected to carry appropriate cover. | Quote early; Machine Credit Rating history may help later. |

## B. Wildlife welfare protocol (draft, to agree with KWS scientists)

1. No driving into the rhino sanctuary. No live public feed of any rhino location.
2. Default viewing distance: stop at least 40 m from an animal before a remote guest is invited to look, and farther for sensitive species. These figures are starting points for a ground vehicle on a road, not aerial stand-off numbers. Tune them with local measurement.
3. Approach along the road only, at a low speed. When wildlife is inside the near radius, cap speed (creep or stop). Do not leave the tarmac or graded track to get a better angle.
4. Mandatory withdrawal: if animals show alertness, agitation, or movement away, the rover backs along the road or holds, and the ranger console is alerted. The remote camera is frozen until the envelope is clear.
5. Daily time limits per circuit, quiet periods around dawn and dusk when many animals move, and a cap on sessions per day.
6. Independent review of the disturbance data; publish results.

## C. Privacy and data

- Blur or drop people and other visitors' vehicle interiors at the edge, before signing or streaming. Do not publish identifiable guests.
- Respect the Kenya Data Protection Act as applicable; appoint a data protection lead.
- Wildlife location data is sensitive: redact coordinates for protected species, delay releases, and grant access per buyer.

## D. Payments and ownership

- Check Kenyan rules on virtual assets and on selling interests in revenue-sharing assets before any mainnet launch or share sale.
- Stablecoin on- and off-ramps must go through licensed providers.
- Keep the community vault on testnet until counsel signs off.

## E. Retired approach (not in the product)

An earlier draft of OFF TOUR used multirotor drones, KCAA unmanned-aircraft rules, and stand-off altitudes drawn from aerial wildlife studies. That path is retired. Drones disturb animals, and Nairobi National Park sits against constrained airspace. Those sources remain in `docs/SOURCES.md` marked superseded so the research trail is honest. Do not plan flights, remote-pilot licences, or per-drone park fees for v1.

## F. Sources

See `SOURCES.md`.
