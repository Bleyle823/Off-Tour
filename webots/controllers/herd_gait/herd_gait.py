"""Leg gait on each GrazingWalker (path is driven by herd supervisor)."""

import math
import sys

from controller import Robot


SPECIES = {
    "horse": {"step_hz": 0.95, "stride": 0.62, "phase": 0.0},
    "deer": {"step_hz": 1.15, "stride": 0.72, "phase": 1.1},
    "cow": {"step_hz": 0.82, "stride": 0.55, "phase": 2.3},
}

LEG_IDS = ("fl", "fr", "rl", "rr")
LEG_PHASE = {"fl": 0.0, "fr": math.pi, "rl": math.pi, "rr": 0.0}


def leg_angles(leg_phase, stride_factor):
    s = math.sin(leg_phase)
    swing = max(0.0, s)
    stance = max(0.0, -s)
    thigh = stride_factor * (0.58 * swing - 0.24 * stance)
    shin = (
        stride_factor * (-0.32 * swing)
        if swing > 0.08
        else stride_factor * (0.55 * stance)
    )
    return thigh, shin


class HerdGait(Robot):
    def __init__(self):
        Robot.__init__(self)
        self.time_step = int(self.getBasicTimeStep())
        species = sys.argv[1] if len(sys.argv) > 1 else "horse"
        cfg = SPECIES.get(species, SPECIES["horse"])
        self.step_hz = cfg["step_hz"]
        self.stride = cfg["stride"]
        self.phase0 = cfg["phase"]
        self.motors = {}
        for leg in LEG_IDS:
            for part in ("thigh", "shin"):
                name = f"leg_{leg}_{part}"
                try:
                    self.motors[name] = self.getDevice(name)
                except Exception:
                    self.motors[name] = None
        if self.motors.get("leg_fl_thigh") is None:
            print(f"[herd_gait] no leg motors on {species}")

    def run(self):
        while self.step(self.time_step) != -1:
            if not self.motors.get("leg_fl_thigh"):
                continue
            t = self.getTime()
            phase = self.phase0 + t * 2.0 * math.pi * self.step_hz
            stride = self.stride * (0.85 + 0.15 * math.sin(phase * 0.5))
            for leg in LEG_IDS:
                lp = phase + LEG_PHASE[leg]
                thigh_a, shin_a = leg_angles(lp, stride)
                thigh_m = self.motors.get(f"leg_{leg}_thigh")
                shin_m = self.motors.get(f"leg_{leg}_shin")
                if thigh_m is not None:
                    thigh_m.setPosition(thigh_a)
                if shin_m is not None:
                    shin_m.setPosition(shin_a)


if __name__ == "__main__":
    HerdGait().run()
