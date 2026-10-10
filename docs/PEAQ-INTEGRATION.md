# peaq integration

Built from the peaq docs (via the peaq MCP) and the peaq blog posts on peaqOS, Escrow and
onchain machines. Where the docs and blogs disagree or a piece is not shipped, it is flagged.

## 1. Principle: nothing safety-critical waits on a chain

Drive control, path-geofence enforcement, proximity limits and the emergency stop run on the
rover. peaq handles identity, bookings, payment, signed data, permissions
and ratings. A failed network call can cancel a booking; it can never move the vehicle.

## 2. Mapping to peaqOS functions

| peaqOS function | Use in OFF TOUR | Status in the docs | What we do |
| --- | --- | --- | --- |
| **Activate** | Each rover gets a peaqID, wallet and Machine NFT. Bond $PEAQ per Economics 2.0 | Live. Registration was marked paused when researched | Check status; use agung testnet first |
| **Scale** | The rover's paired agent buys charging, compute (species ID), connectivity; spend limits per transaction and per day; x402 for micro-payments | Live | Pair an agent with a strict delegation policy; community charging splits revenue |
| **Stream** | Edge Agent signs, encrypts and chunks detections and footage; Data Event Map redacts fields; buyers get access grants | Live. Buyer purchase routes return 404 today. Edge Agent is a ROS 2 node, which suits a companion computer on the rover | Build signing and redaction now; mock the purchase step and label it |
| **Qualify** | Machine Credit Rating from patrol, payment and data events | Live | Submit events with the highest honest trust level; hardware-signed weighs most |
| **Verify** | Chip attestation that the rover's secure element is genuine | Beta; one chip family (Infineon OPTIGA Trust M Express), peaq mainnet only | Consider later; not required for v1 |
| **Monetize** | Selling spare compute | v1 is compute only via Akash | Not used |
| **Tokenize** | Fractional ownership | Not shipped | Build our own vault (see section 6) |

## 3. Booking and settlement flow (peaq Escrow)

Based on the Escrow docs: ClaimRegistry on peaq, BaseEscrow on Base, LayerZero relaying funding
and completion, claim states Created, Accepted, Funded, Completed.

1. **Register.** The rover's agent card (ERC-8004) and the buyer's identity exist on peaq.
2. **Create claim.** The participant (or a school, sponsor or operator on their behalf) creates
   a purchase claim on peaq naming the rover as seller, with the session price and a
   deadline. Both sides lock a stake.
3. **Accept.** The operator's agent accepts after checking that an approved circuit window,
   weather, the trained path, and the rover are available. Claim becomes Accepted.
4. **Fund.** The buyer deposits stablecoin into BaseEscrow on Base. LayerZero relays it; the
   claim becomes Funded on peaq.
5. **Drive.** The rover follows the trained path by itself. There is no driver aboard. The Edge Agent
   signs the patrol log and data chunks.
6. **Validate.** A KWS ranger posts an attestation (Validation
   Registry) that the session was delivered inside the approved envelope.
7. **Release.** Payment releases on Base and completion syncs to peaq; stakes return. The docs
   describe the buyer calling release; the Escrow blog says the seller does. Read the contract
   before designing around either.
8. **Split.** Revenue lands in the vault and is split by agreed percentages (KWS share,
   operator, community, reserve).
9. **Reputation.** The participant leaves feedback in the Reputation Registry; the session
   becomes events that feed the Machine Credit Rating.

Failure paths to design: weather or approval cancellation (refund, stakes returned), safety
abort mid-session (partial delivery rules), and disputes (freeze, human resolution).

## 4. Permits as checkable facts

KWS remains the legal authority for park use; the chain only makes approvals easy to check.
Pattern, which the "access control: clearance before takeoff" idea in the peaqOS blog
describes (partners build the gate, not a peaq product):

- The authority issues a signed permit for rover X, circuit Y, window Z.
- A validation record points to it on peaq.
- The ranger console checks the record before the session starts, and the rover refuses to
  leave the staging point outside the permit. Paper permits still apply in parallel.

## 5. Data policy (Stream Data Event Map)

The Edge Agent applies field rules before signing: `include`, `exclude`, `encrypt`,
`anonymize`. Proposed policy:

| Data | Rule | Who can access |
| --- | --- | --- |
| Species, count, timestamp | include | Researchers, guides (non-sensitive species) |
| Coordinates for rhino and other protected species | encrypt, release delayed | KWS only |
| Coordinates for common species | coarsened | Guides, after a delay |
| People and vehicle interiors | drop or blur before signing | Nobody |
| Patrol log (distance, speed, path exits, aborts) | include | KWS, regulators, public summary |
| Raw video | encrypt | KWS and the booking participant |

Signing proves which rover produced the data and that it was not altered; it does not prove
the animal was where the label says. Add validator checks and ranger spot-audits.

## 6. Community co-ownership

peaq's Tokenize is not shipped. Under Economics 2.0 the Machine NFT is an ERC-721 whose token
ID is the machine ID, and transferring it transfers ownership of the machine. The same vault
pattern planned for the sibling `moonad` project applies:

1. Lock the rover's Machine NFT in a vault contract.
2. Issue ERC-20 shares to the community and operator.
3. Deposit session revenue; distribute pro rata with accounting that follows share transfers.

Treat this as a testnet prototype until Kenyan counsel clears it. Consider a non-transferable
community benefit share before any tradable token.

## 7. Payments in Kenya

Many Kenyans pay with M-Pesa. A practical route is a licensed provider that converts mobile
money to stablecoin for the Base deposit, so schools and locals never touch a wallet. This is
an integration to scope with a provider, not a feature that exists.

## 8. Live versus mocked in Phase 0

| Piece | Phase 0 |
| --- | --- |
| Path and proximity envelope, patrol log | Real code (`sim/proximity.py`, `sim/patrol_log.py`) |
| peaqID and wallet on agung | Real |
| Escrow booking | Real on agung and Base testnets if registration allows; else mocked |
| Data signing and redaction | Real signing; mocked buyer purchase |
| Permit attestation | Mocked authority key |
| Vault payout | Real contract on testnet |
| Rover, detector, link | Simulated |
