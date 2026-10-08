"""Mock escrow booking for a Remote Seat session.

Mirrors peaq Escrow claim states from the docs:
Created -> Accepted -> Funded -> Completed (or Cancelled / Disputed).

No chain calls; this lets us wire the product flow before agung integration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ClaimStatus(str, Enum):
    CREATED = "Created"
    ACCEPTED = "Accepted"
    FUNDED = "Funded"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    DISPUTED = "Disputed"


@dataclass
class SessionClaim:
    claim_id: str
    buyer_id: str
    seller_machine_id: str
    price_usdc_cents: int
    deadline_iso: str
    status: ClaimStatus = ClaimStatus.CREATED
    buyer_stake_cents: int = 0
    seller_stake_cents: int = 0
    validation_ref: Optional[str] = None
    history: List[str] = field(default_factory=list)

    def _log(self, msg: str) -> None:
        self.history.append("%s: %s" % (self.status.value, msg))


class SessionRegistry:
    def __init__(self) -> None:
        self._claims: dict[str, SessionClaim] = {}

    def create(
        self,
        claim_id: str,
        buyer_id: str,
        seller_machine_id: str,
        price_usdc_cents: int,
        deadline_iso: str,
        buyer_stake_cents: int,
    ) -> SessionClaim:
        if claim_id in self._claims:
            raise ValueError("claim exists")
        c = SessionClaim(
            claim_id=claim_id,
            buyer_id=buyer_id,
            seller_machine_id=seller_machine_id,
            price_usdc_cents=price_usdc_cents,
            deadline_iso=deadline_iso,
            buyer_stake_cents=buyer_stake_cents,
        )
        c._log("created")
        self._claims[claim_id] = c
        return c

    def get(self, claim_id: str) -> SessionClaim:
        return self._claims[claim_id]

    def accept(self, claim_id: str, seller_stake_cents: int) -> SessionClaim:
        c = self.get(claim_id)
        if c.status != ClaimStatus.CREATED:
            raise ValueError("invalid state for accept: %s" % c.status)
        c.seller_stake_cents = seller_stake_cents
        c.status = ClaimStatus.ACCEPTED
        c._log("seller accepted")
        return c

    def fund(self, claim_id: str) -> SessionClaim:
        c = self.get(claim_id)
        if c.status != ClaimStatus.ACCEPTED:
            raise ValueError("invalid state for fund: %s" % c.status)
        c.status = ClaimStatus.FUNDED
        c._log("escrow funded (mock BaseEscrow)")
        return c

    def complete(self, claim_id: str, validation_ref: str) -> SessionClaim:
        c = self.get(claim_id)
        if c.status != ClaimStatus.FUNDED:
            raise ValueError("invalid state for complete: %s" % c.status)
        c.validation_ref = validation_ref
        c.status = ClaimStatus.COMPLETED
        c._log("payment released; stakes returned (mock)")
        return c

    def cancel(self, claim_id: str, reason: str) -> SessionClaim:
        c = self.get(claim_id)
        if c.status in (ClaimStatus.COMPLETED, ClaimStatus.CANCELLED):
            raise ValueError("cannot cancel: %s" % c.status)
        c.status = ClaimStatus.CANCELLED
        c._log("cancelled: %s" % reason)
        return c
