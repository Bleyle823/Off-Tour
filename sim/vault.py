"""Mock revenue split after a completed session (community vault)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class SplitPolicy:
    """Percentages must sum to 100."""

    kws_pct: float = 15.0
    operator_pct: float = 35.0
    community_pct: float = 30.0
    platform_pct: float = 10.0
    reserve_pct: float = 10.0

    def validate(self) -> None:
        total = self.kws_pct + self.operator_pct + self.community_pct + self.platform_pct + self.reserve_pct
        if abs(total - 100.0) > 0.01:
            raise ValueError("split must sum to 100, got %.2f" % total)


def split_revenue(amount_cents: int, policy: SplitPolicy) -> Dict[str, int]:
    policy.validate()
    return {
        "kws": int(amount_cents * policy.kws_pct / 100),
        "operator": int(amount_cents * policy.operator_pct / 100),
        "community_vault": int(amount_cents * policy.community_pct / 100),
        "platform": int(amount_cents * policy.platform_pct / 100),
        "reserve": int(amount_cents * policy.reserve_pct / 100),
    }
