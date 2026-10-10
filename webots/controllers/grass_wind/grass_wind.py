"""Wind sway by rotating the world-level SAVANNAH_TALL_GRASS layer."""

import math

from controller import Supervisor


class GrassWindSupervisor(Supervisor):
    def __init__(self):
        Supervisor.__init__(self)
        self.time_step = int(self.getBasicTimeStep())
        self.rotation = None
        self.wind_heading = math.radians(35)
        self.wx = math.cos(self.wind_heading)
        self.wy = math.sin(self.wind_heading)

    def run(self):
        while self.step(self.time_step) != -1:
            if self.rotation is None:
                layer = self.getFromDef("SAVANNAH_TALL_GRASS")
                if layer is not None:
                    self.rotation = layer.getField("rotation")
                    if self.rotation is not None:
                        print("[grass_wind] layer rotation sway active")
                if self.rotation is None:
                    continue
            t = self.getTime()
            gust = 0.55 + 0.45 * math.sin(t * 0.17 + 0.8)
            wave = math.sin(t * 2.0)
            angle = gust * (0.12 * wave + 0.04 * math.sin(t * 5.0))
            ax = -self.wy
            ay = self.wx
            self.rotation.setSFRotation([ax, ay, 0, angle])


if __name__ == "__main__":
    GrassWindSupervisor().run()
