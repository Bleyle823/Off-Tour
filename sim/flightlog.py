"""Deprecated name for the patrol log. Prefer `patrol_log`."""

try:
    from patrol_log import GENESIS, PatrolLog as FlightLog, verify
except ImportError:
    from .patrol_log import GENESIS, PatrolLog as FlightLog, verify

__all__ = ["GENESIS", "FlightLog", "verify"]
