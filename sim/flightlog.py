"""Tamper-evident flight log (hash chain).

Each entry commits to the previous entry's hash, so altering or removing any
entry breaks verification of everything after it.

This is NOT a signature. In the real system the peaqOS Edge Agent signs entries
with the machine's key; here a hash chain stands in so the log format and the
verification logic can be built and tested first.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List

GENESIS = "0" * 64


def _digest(seq: int, ts: str, payload: Dict[str, Any], prev_hash: str) -> str:
    body = json.dumps(
        {"seq": seq, "ts": ts, "payload": payload, "prev": prev_hash},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


class FlightLog:
    def __init__(self) -> None:
        self.entries: List[Dict[str, Any]] = []

    def append(self, ts: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        prev = self.entries[-1]["hash"] if self.entries else GENESIS
        seq = len(self.entries)
        entry = {"seq": seq, "ts": ts, "payload": payload, "prev": prev,
                 "hash": _digest(seq, ts, payload, prev)}
        self.entries.append(entry)
        return entry

    def head(self) -> str:
        """Hash to anchor on-chain (or put in a signed session summary)."""
        return self.entries[-1]["hash"] if self.entries else GENESIS


def verify(entries: List[Dict[str, Any]]) -> bool:
    prev = GENESIS
    for i, e in enumerate(entries):
        if e.get("seq") != i or e.get("prev") != prev:
            return False
        if e.get("hash") != _digest(e["seq"], e["ts"], e["payload"], e["prev"]):
            return False
        prev = e["hash"]
    return True
