"""Remote camera intents (participants never command the rover).

Intents apply only while the proximity envelope is OK: the rover is on the
approved path, at viewing distance, and not being told to slow or retreat.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

try:
    import proximity as s
except ModuleNotFoundError:
    from . import proximity as s


@dataclass(frozen=True)
class CameraState:
    pan_deg: float = 0.0
    tilt_deg: float = 0.0
    zoom: float = 1.0


@dataclass(frozen=True)
class CameraIntent:
    """Delta request from a remote participant."""

    pan_delta_deg: float = 0.0
    tilt_delta_deg: float = 0.0
    zoom_delta: float = 0.0


@dataclass
class CameraController:
    max_pan_deg: float = 120.0
    max_tilt_deg: float = 45.0
    min_zoom: float = 1.0
    max_zoom: float = 8.0
    max_delta_per_intent: float = 15.0
    state: CameraState = CameraState()
    intents_rejected: int = 0
    intents_applied: int = 0

    def apply_intent(
        self,
        intent: CameraIntent,
        envelope: s.Decision,
    ) -> Tuple[bool, str]:
        if not s.camera_intent_allowed(envelope):
            self.intents_rejected += 1
            return False, "envelope not OK: %s" % envelope.action

        for name, delta in (
            ("pan", intent.pan_delta_deg),
            ("tilt", intent.tilt_delta_deg),
            ("zoom", intent.zoom_delta),
        ):
            if abs(delta) > self.max_delta_per_intent:
                self.intents_rejected += 1
                return False, "%s delta %.1f exceeds limit" % (name, delta)

        pan = max(-self.max_pan_deg, min(self.max_pan_deg, self.state.pan_deg + intent.pan_delta_deg))
        tilt = max(-self.max_tilt_deg, min(self.max_tilt_deg, self.state.tilt_deg + intent.tilt_delta_deg))
        zoom = max(self.min_zoom, min(self.max_zoom, self.state.zoom + intent.zoom_delta))
        self.state = CameraState(pan, tilt, zoom)
        self.intents_applied += 1
        return True, "ok"
