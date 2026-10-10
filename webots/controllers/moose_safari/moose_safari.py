"""OFF TOUR path follower for a Clearpath Moose.

The rover is trained on the designated tourist self-drive circuit and
skid-steers that centerline unless someone is driving it. Click the 3D
view, then use W/A/S/D to drive. Releasing those keys returns to the circuit.
Arrow keys still aim the mast. +/- or Page Up/Down zoom.

Open webots/worlds/off_tour_savannah.wbt in Webots R2025a.
"""

import math
import sys
from pathlib import Path

from controller import Keyboard, Robot

from path_follow import WaypointFollower, load_waypoints


def clamp(value, value_min, value_max):
    return min(max(value, value_min), value_max)


# World-frame sites matching SavannahRange bushfires (range translation -40, -40).
FIRE_SITES = {
    "bushfire_savannah": (-26.0, 12.0, 210.0, 0.55),
    "bushfire_woodland": (22.0, -18.0, 240.0, 0.7),
}

HOTSPOT_C = 120.0
WARNING_C = 180.0
CRITICAL_C = 250.0

ANIMAL_MODELS = {"horse", "deer", "cow"}
VIEWING_M = 8.0
LOOK_RANGE_M = 45.0
LOOK_HOLD_S = 6.0
COOLDOWN_S = 12.0
DRIVE_SPEED = 6.0
SPIN = 10.0
MAX_WHEEL = 8.0

YAW_LIMIT = 2.5
PITCH_LIMIT_DOWN = -0.65
PITCH_LIMIT_UP = 0.5
AIM_GAIN = 0.35
FOV_STEP = 0.04
PAN_STEP = 0.03
TILT_STEP = 0.02

KEY_PAGE_UP = Keyboard.PAGEUP
KEY_PAGE_DOWN = Keyboard.PAGEDOWN
KEY_LEFT = Keyboard.LEFT
KEY_RIGHT = Keyboard.RIGHT
KEY_UP = Keyboard.UP
KEY_DOWN = Keyboard.DOWN


def fire_level(brightness_c, smoke, wind_ms=6.0, humidity_pct=28.0):
    dry_boost = 1.0 + max(0.0, (40.0 - humidity_pct) / 100.0)
    effective = brightness_c * dry_boost
    if wind_ms >= 8.0 and effective >= HOTSPOT_C:
        effective += 15.0
    if effective >= CRITICAL_C or smoke >= 0.70:
        return "critical", "critical thermal and/or smoke signature"
    if effective >= WARNING_C or smoke >= 0.45:
        return "warning", "elevated heat or smoke; ranger dispatch recommended"
    if effective >= HOTSPOT_C:
        return "watch", "localized hotspot; monitor and correlate with ground reports"
    return "none", ""


class MooseSafari(Robot):
    def __init__(self):
        Robot.__init__(self)
        self.time_step = int(self.getBasicTimeStep())
        self.camera = self.getDevice("camera")
        self.camera.enable(self.time_step)
        if self.camera.hasRecognition():
            self.camera.recognitionEnable(self.time_step)
        self.fov_max = self.camera.getMaxFov()
        self.fov_min = self.camera.getMinFov()
        self.fov_zoom_enabled = abs(self.fov_max - self.fov_min) > 1e-6
        self.fov = self.fov_max
        if self.fov_zoom_enabled:
            self.camera.setFov(self.fov)
        self.gps = self.getDevice("gps")
        self.gps.enable(self.time_step)
        self.compass = self.getDevice("compass")
        self.compass.enable(self.time_step)
        self.front_lidar = self.getDevice("front lidar")
        self.front_lidar.enable(self.time_step)
        self.velodyne = self.getDevice("velodyne")
        self.velodyne.enable(self.time_step)
        self.radar = self.getDevice("front radar")
        self.radar.enable(self.time_step)
        for name in (
            "imu accelerometer",
            "imu gyro",
            "imu inertial_unit",
        ):
            device = self.getDevice(name)
            device.enable(self.time_step)
        self.keyboard = Keyboard()
        self.keyboard.enable(self.time_step)
        self.left = []
        self.right = []
        for index in range(1, 5):
            motor = self.getDevice("left motor %d" % index)
            motor.setPosition(float("inf"))
            motor.setVelocity(0.0)
            self.left.append(motor)
        for index in range(1, 5):
            motor = self.getDevice("right motor %d" % index)
            motor.setPosition(float("inf"))
            motor.setVelocity(0.0)
            self.right.append(motor)
        self.yaw_motor = self.getDevice("camera yaw")
        self.pitch_motor = self.getDevice("camera pitch")
        self.cam_yaw = 0.0
        self.cam_pitch = 0.0
        self.manual_camera = False
        self.driving = False
        points, stop_at_end = load_waypoints(Path(__file__).resolve().parent)
        self.follower = WaypointFollower(points, stop_at_end=stop_at_end)
        print("[moose] loaded %d waypoints (stop_at_end=%s)" % (len(points), stop_at_end))
        self.looking = False
        self.look_left = 0.0
        self.cooldown = 0.0
        self.reported = set()
        self.x = 0.0
        self.y = 0.0

    def set_speed(self, left, right):
        left = clamp(left, -MAX_WHEEL, MAX_WHEEL)
        right = clamp(right, -MAX_WHEEL, MAX_WHEEL)
        for motor in self.left:
            motor.setVelocity(left)
        for motor in self.right:
            motor.setVelocity(right)

    def set_mast(self, yaw, pitch):
        self.cam_yaw = clamp(yaw, -YAW_LIMIT, YAW_LIMIT)
        self.cam_pitch = clamp(pitch, PITCH_LIMIT_DOWN, PITCH_LIMIT_UP)
        self.yaw_motor.setPosition(self.cam_yaw)
        self.pitch_motor.setPosition(self.cam_pitch)

    def handle_keyboard(self):
        key = self.keyboard.getKey()
        zoomed = False
        panned = False
        forward = 0.0
        turn = 0.0
        while key != -1:
            base = key & 0xFFFF
            if self.fov_zoom_enabled and base in (ord("+"), ord("="), KEY_PAGE_UP):
                self.fov = clamp(self.fov - FOV_STEP, self.fov_min, self.fov_max)
                zoomed = True
            elif self.fov_zoom_enabled and base in (ord("-"), ord("_"), KEY_PAGE_DOWN):
                self.fov = clamp(self.fov + FOV_STEP, self.fov_min, self.fov_max)
                zoomed = True
            elif base == KEY_LEFT:
                self.cam_yaw += PAN_STEP
                panned = True
            elif base == KEY_RIGHT:
                self.cam_yaw -= PAN_STEP
                panned = True
            elif base == KEY_UP:
                self.cam_pitch += TILT_STEP
                panned = True
            elif base == KEY_DOWN:
                self.cam_pitch -= TILT_STEP
                panned = True
            elif base in (ord("W"), ord("w")):
                forward += DRIVE_SPEED
            elif base in (ord("S"), ord("s")):
                forward -= DRIVE_SPEED
            elif base in (ord("A"), ord("a")):
                turn += 1.0
            elif base in (ord("D"), ord("d")):
                turn -= 1.0
            key = self.keyboard.getKey()
        if zoomed:
            self.camera.setFov(self.fov)
        if panned:
            self.manual_camera = True
            self.set_mast(self.cam_yaw, self.cam_pitch)
        driving = forward != 0.0 or turn != 0.0
        if driving and not self.driving:
            print("[moose] manual drive (release W/A/S/D to resume the trained circuit)")
        elif self.driving and not driving:
            print("[moose] resume trained circuit")
        self.driving = driving
        if driving:
            # Opposite track speeds. A small differential just plows an 8-wheeler straight.
            yaw = 0.0 if turn == 0.0 else math.copysign(SPIN, turn)
            self.set_speed(forward - yaw, forward + yaw)
        return panned

    def read_pose(self):
        position = self.gps.getValues()
        self.x = position[0]
        self.y = position[1]
        north = self.compass.getValues()
        return math.atan2(north[0], north[1])

    def path_blocked(self):
        ranges = self.front_lidar.getRangeImage()
        if not ranges:
            return False
        resolution = self.front_lidar.getHorizontalResolution()
        if resolution <= 0:
            return False
        fov = self.front_lidar.getFov()
        half = 0.4
        center = resolution // 2
        span = max(1, int(half / fov * resolution))
        start = max(0, center - span)
        end = min(resolution, center + span)
        nearest = min(ranges[start:end])
        return nearest < 2.5

    def follow_path(self, robot_angle):
        if self.follower.finished:
            self.set_speed(0.0, 0.0)
            return
        left, right, advanced = self.follower.command(
            self.x, self.y, robot_angle, blocked=self.path_blocked()
        )
        if advanced is not None:
            print("[moose] next waypoint (%.1f, %.1f)" % advanced)
        if self.follower.finished:
            print("[moose] circuit complete; holding")
        self.set_speed(left, right)

    def scan_animals(self):
        if not self.camera.hasRecognition():
            return None
        best = None
        best_dist = 1e9
        for obj in self.camera.getRecognitionObjects():
            model = obj.getModel()
            if model not in ANIMAL_MODELS:
                continue
            pos = obj.getPosition()
            forward = -pos[2]
            right = pos[0]
            up = pos[1]
            dist = math.hypot(forward, right)
            if dist < best_dist:
                best_dist = dist
                best = (model, forward, right, up, dist)
        return best

    def aim_mast(self, sighting):
        _model, forward, right, up, _dist = sighting
        yaw_error = math.atan2(right, max(forward, 0.05))
        horizontal = math.hypot(forward, right)
        pitch_error = math.atan2(up, max(horizontal, 0.05))
        self.set_mast(self.cam_yaw + AIM_GAIN * yaw_error, self.cam_pitch + AIM_GAIN * pitch_error)

    def center_mast(self):
        self.set_mast(self.cam_yaw * 0.9, self.cam_pitch * 0.9)

    def scan_fires(self):
        seen = set()
        if self.camera.hasRecognition():
            for obj in self.camera.getRecognitionObjects():
                model = obj.getModel()
                if model:
                    seen.add(model)
        for name, (fx, fy, temp_c, smoke) in FIRE_SITES.items():
            dist = math.hypot(self.x - fx, self.y - fy)
            visible = name in seen or dist < 28.0
            if not visible:
                continue
            brightness = temp_c * clamp(1.15 - dist / 80.0, 0.55, 1.1)
            level, reason = fire_level(brightness, smoke)
            key = (name, level)
            if level == "none" or key in self.reported:
                continue
            self.reported.add(key)
            print(
                "[RANGER ONLY] fire_alert rover=%s site=%s level=%s x=%.1f y=%.1f "
                "brightness_c=%.0f reason=%s"
                % (self.getName(), name, level, fx, fy, brightness, reason)
            )

    def run(self):
        dt = self.time_step / 1000.0
        print(
            "[moose] trained circuit. W/A/S/D drives; arrows aim the camera; +/- zooms"
        )
        while self.step(self.time_step) != -1:
            panned = self.handle_keyboard()
            robot_angle = self.read_pose()
            self.scan_fires()
            if self.driving:
                continue
            sighting = self.scan_animals()
            if self.cooldown > 0:
                self.cooldown -= dt
            if self.looking:
                self.look_left -= dt
                self.set_speed(0.0, 0.0)
                if sighting and self.look_left > 0:
                    if not panned:
                        self.aim_mast(sighting)
                else:
                    self.looking = False
                    self.manual_camera = False
                    self.cooldown = COOLDOWN_S
                    print("[moose] resume trained circuit")
                continue
            if (
                self.cooldown <= 0
                and sighting is not None
                and VIEWING_M < sighting[4] < LOOK_RANGE_M
            ):
                self.looking = True
                self.look_left = LOOK_HOLD_S
                self.set_speed(0.0, 0.0)
                print("[moose] stop on path to view %s at %.1f m" % (sighting[0], sighting[4]))
                if not panned:
                    self.aim_mast(sighting)
                continue
            self.follow_path(robot_angle)
            if not panned and not self.manual_camera:
                self.center_mast()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("[moose] ignoring extra args; the trained circuit is fixed")
    MooseSafari().run()
