"""Supervisor: herd paths and body bob (leg gait is herd_gait on each animal)."""

import math

from controller import Supervisor


HERD = [
    {
        "def": "HERD_HORSE",
        "path": [(-28, 6), (-22, 10), (-16, 8), (-20, 2), (-26, 4)],
        "speed": 1.05,
        "phase": 0.0,
        "step_hz": 0.95,
        "stride": 0.62,
    },
    {
        "def": "HERD_DEER",
        "path": [(-16, 16), (-12, 12), (-8, 16), (-14, 20)],
        "speed": 1.25,
        "phase": 1.1,
        "step_hz": 1.15,
        "stride": 0.72,
    },
    {
        "def": "HERD_COW",
        "path": [(-30, 2), (-24, 0), (-18, 4), (-24, 8), (-30, 6)],
        "speed": 0.85,
        "phase": 2.3,
        "step_hz": 0.82,
        "stride": 0.55,
    },
]

def advance_on_path(path, dist):
    if len(path) < 2:
        return path[0][0], path[0][1], 0.0
    total = 0.0
    segments = []
    for i in range(len(path)):
        x0, y0 = path[i]
        x1, y1 = path[(i + 1) % len(path)]
        seg = math.hypot(x1 - x0, y1 - y0)
        segments.append((seg, x0, y0, x1, y1))
        total += seg
    if total < 1e-6:
        return path[0][0], path[0][1], 0.0
    dist = dist % total
    for seg, x0, y0, x1, y1 in segments:
        if dist > seg:
            dist -= seg
            continue
        t = dist / max(seg, 1e-6)
        return (
            x0 + (x1 - x0) * t,
            y0 + (y1 - y0) * t,
            math.atan2(y1 - y0, x1 - x0),
        )
    return path[-1][0], path[-1][1], 0.0


class HerdSupervisor(Supervisor):
    def __init__(self):
        Supervisor.__init__(self)
        self.time_step = int(self.getBasicTimeStep())
        self.dt = self.time_step / 1000.0
        self.step(self.time_step)
        self.members = []
        for spec in HERD:
            robot = self.getFromDef(spec["def"])
            if robot is None:
                print(f"[herd] missing DEF {spec['def']}")
                continue
            self.members.append(
                {
                    **spec,
                    "trans": robot.getField("translation"),
                    "rot": robot.getField("rotation"),
                    "base_z": robot.getField("translation").getSFVec3f()[2],
                    "distance": 0.0,
                }
            )

    def run(self):
        while self.step(self.time_step) != -1:
            t = self.getTime()
            for m in self.members:
                phase = m["phase"] + t * 2.0 * math.pi * m["step_hz"]
                m["distance"] += m["speed"] * self.dt
                x, y, heading = advance_on_path(m["path"], m["distance"])
                bob = 0.035 * math.sin(phase * 2.0)
                m["trans"].setSFVec3f([x, y, m["base_z"] + bob])
                sway = 0.02 * math.sin(phase)
                roll = 0.035 * math.sin(phase + math.pi / 2)
                m["rot"].setSFRotation([0, 0, 1, heading + sway + roll])


if __name__ == "__main__":
    HerdSupervisor().run()
