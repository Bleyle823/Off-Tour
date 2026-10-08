"""Forest / bushfire detection from thermal and smoke cues (Ranger Eye).

Thresholds are starting points for simulation; KWS fire protocols override in the field.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class FireRiskLevel(str, Enum):
    NONE = "none"
    WATCH = "watch"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ThermalSample:
    lat: float
    lon: float
    brightness_temp_c: float
    smoke_index: float = 0.0  # 0..1 heuristic from vision stack


# Dry-season bush/grass fire heuristics (tune with KWS).
_HOTSPOT_C = 120.0
_WARNING_C = 180.0
_CRITICAL_C = 250.0
_SMOKE_WARNING = 0.45
_SMOKE_CRITICAL = 0.70


@dataclass(frozen=True)
class FireAssessment:
    level: FireRiskLevel
    lat: float
    lon: float
    reason: str
    brightness_temp_c: float
    smoke_index: float


def assess_fire_from_thermal(
    samples: List[ThermalSample],
    wind_ms: float,
    *,
    humidity_pct: Optional[float] = None,
) -> List[FireAssessment]:
    """Return one assessment per sample that exceeds watch threshold."""
    out: List[FireAssessment] = []
    humidity = humidity_pct if humidity_pct is not None else 35.0
    dry_boost = 1.0 + max(0.0, (40.0 - humidity) / 100.0)

    for s in samples:
        effective_c = s.brightness_temp_c * dry_boost
        if wind_ms >= 8.0 and effective_c >= _HOTSPOT_C:
            effective_c += 15.0

        level = FireRiskLevel.NONE
        reason = ""
        if effective_c >= _CRITICAL_C or s.smoke_index >= _SMOKE_CRITICAL:
            level = FireRiskLevel.CRITICAL
            reason = "critical thermal and/or smoke signature"
        elif effective_c >= _WARNING_C or s.smoke_index >= _SMOKE_WARNING:
            level = FireRiskLevel.WARNING
            reason = "elevated heat or smoke; ranger dispatch recommended"
        elif effective_c >= _HOTSPOT_C:
            level = FireRiskLevel.WATCH
            reason = "localized hotspot; monitor and correlate with ground reports"

        if level != FireRiskLevel.NONE:
            out.append(
                FireAssessment(
                    level=level,
                    lat=s.lat,
                    lon=s.lon,
                    reason=reason,
                    brightness_temp_c=s.brightness_temp_c,
                    smoke_index=s.smoke_index,
                )
            )
    return out
