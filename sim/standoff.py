"""Deprecated name for the proximity envelope. Prefer `proximity`."""

try:
    from proximity import (  # noqa: F401
        ABORT,
        OK,
        RETREAT,
        SLOW,
        Animal,
        Config,
        Decision,
        ExclusionZone,
        PathPoint,
        RoverState,
        camera_intent_allowed,
        distance_to_path_m,
        evaluate,
        haversine_m,
        inside_corridor,
    )
except ImportError:
    from .proximity import (  # noqa: F401
        ABORT,
        OK,
        RETREAT,
        SLOW,
        Animal,
        Config,
        Decision,
        ExclusionZone,
        PathPoint,
        RoverState,
        camera_intent_allowed,
        distance_to_path_m,
        evaluate,
        haversine_m,
        inside_corridor,
    )
