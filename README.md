# Off-Tour 

**Tele-present safari.** A KCAA-licensed, ranger-supervised, mostly autonomous drone that
watches wildlife in Nairobi National Park from a respectful distance, while people anywhere
take a "remote seat" to look around, learn and pay. Its sightings are signed at the source,
its bookings are escrowed, its safety record builds a public credit rating, and its income
is shared with the park and the community, all on [peaq](https://www.peaq.xyz).

> Status: plan and first prototype. Nothing here has regulatory approval yet. Read
> `docs/COMPLIANCE.md` before anyone flies anything.

## The one-paragraph idea

Nairobi National Park is the world's only national park inside a capital city: 117 km², about
460,000 visitors in 2025, black and white rhino, lion, leopard, giraffe, buffalo, no
resident elephants, and jets landing at JKIA and Wilson over the fence. Most people who love
wildlife will never visit it, and visitors in vehicles see only a sliver of it. Off-Safari
adds a drone that finds and follows animals at a safe stand-off distance, streams to remote
participants who steer the *camera* (never the aircraft), and doubles as a conservation
tool for rangers: thermal patrols, fence-line checks, carcass and snare detection. A human
licensed pilot always keeps command. peaq gives the drone a verifiable identity, a wallet,
escrowed bookings, signed data, and a credit record.

## Why peaq (and what each piece does here)

| Need | peaq piece | Notes |
| --- | --- | --- |
| The drone is an accountable economic actor | peaqOS Activate: peaqID, wallet, Machine NFT | Registration was marked paused in the docs when researched. Check first. |
| Booking and paying for a session | peaq Escrow (ERC-8004, ClaimRegistry, BaseEscrow, LayerZero) | Buyer funds on Base, claim state lives on peaq |
| Footage and detections nobody can fake | peaqOS Stream: Edge Agent signs and encrypts at capture (ROS 2) | Field rules redact protected species locations |
| Drone buys power, compute, connectivity | peaqOS Scale (agent pairing, spend limits, x402) | Charging-pad revenue splits across co-owners |
| Permits and safety as checkable facts | ERC-8004 Validation and Reputation registries | KWS/KCAA authorizations recorded as attestations |
| A safety and reliability record | peaqOS Qualify (Machine Credit Rating) | Needed for insurance and financing |
| Community co-ownership | Own vault contract (peaq's Tokenize is not shipped) | Same pattern as the sibling `moonad` project |

Detail in `docs/PEAQ-INTEGRATION.md`.

## Repo map

- `docs/PLAN.md` - the project plan: users, product, phases, workstreams, milestones, risks
- `docs/COMPLIANCE.md` - aviation, park, privacy and wildlife checklists, with sources
- `docs/PEAQ-INTEGRATION.md` - architecture, booking flow, data policy, what is live vs mocked
- `docs/SOURCES.md` - every external fact used, with links and dates
- `docs/NEXT-STEPS.md` - engineering and regulatory queue
- `templates/kws-intro.md` - draft letter to KWS (edit before sending)
- `sim/` - product logic prototype (pure Python, no dependencies):
  - `standoff.py` - safety envelope (outranks pilot and remote users)
  - `flightlog.py` - hash-chained flight log (placeholder for Stream signing)
  - `session.py` - mock peaq Escrow claim lifecycle
  - `camera.py` - remote camera intents only
  - `redaction.py` - Stream-style field rules (rhino coords, people blur)
  - `vault.py` - revenue split after a completed session
  - `demo_session.py` - end-to-end mock run

```bash
cd C:\Users\Omen\Desktop\Off-Safari-main
python -m unittest discover -s sim -v
python -m sim.demo_session
```
