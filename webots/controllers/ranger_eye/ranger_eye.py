"""OFF TOUR Ranger Eye controller for the Mavic 2 Pro.

Patrols a savannah transect and reports bushfires. Fire levels follow the same
watch / warning / critical idea as sim/conservation/fire.py. Alerts are printed
for the ranger console only; they are not a public feed.

Open webots/worlds/off_tour_savannah.wbt in Webots R2025a.
"""

import math
import sys

from controller import Robot


def clamp(value, value_min, value_max):
    return min(max(value, value_min), value_max)


# Known bushfire sites in the savannah world (x, y, brightness C, smoke 0..1).
# World-frame sites. Terrain origin is (-40, -40); local fire points are (14, 52) and (62, 22).
FIRE_SITES = {
    "bushfire_savannah": (-26.0, 12.0, 210.0, 0.55),
    "bushfire_woodland": (22.0, -18.0, 240.0, 0.7),
}

HOTSPOT_C = 120.0
WARNING_C = 180.0
CRITICAL_C = 250.0


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


class RangerEye(Robot):
    K_VERTICAL_THRUST = 68.5
    K_VERTICAL_OFFSET = 0.6
    K_VERTICAL_P = 3.0
    K_ROLL_P = 50.0
    K_PITCH_P = 30.0
    MAX_YAW_DISTURBANCE = 0.4
    MAX_PITCH_DISTURBANCE = -1
    TARGET_PRECISION = 1.5

    def __init__(self, role):
        Robot.__init__(self)
        self.role = role
        self.time_step = int(self.getBasicTimeStep())
        self.camera = self.getDevice("camera")
        self.camera.enable(self.time_step)
        if self.camera.hasRecognition():
            self.camera.recognitionEnable(self.time_step)
        self.imu = self.getDevice("inertial unit")
        self.imu.enable(self.time_step)
        self.gps = self.getDevice("gps")
        self.gps.enable(self.time_step)
        self.gyro = self.getDevice("gyro")
        self.gyro.enable(self.time_step)
        self.front_left_motor = self.getDevice("front left propeller")
        self.front_right_motor = self.getDevice("front right propeller")
        self.rear_left_motor = self.getDevice("rear left propeller")
        self.rear_right_motor = self.getDevice("rear right propeller")
        self.camera_pitch_motor = self.getDevice("camera pitch")
        self.camera_pitch_motor.setPosition(0.7)
        for motor in (
            self.front_left_motor,
            self.front_right_motor,
            self.rear_left_motor,
            self.rear_right_motor,
        ):
            motor.setPosition(float("inf"))
            motor.setVelocity(1)
        self.current_pose = [0.0] * 6
        self.target_position = [0.0, 0.0, 0.0]
        self.target_index = 0
        self.target_altitude = 18.0 if role == "ranger" else 22.0
        self.waypoints = (
            [[-24, 14], [-18, -8], [6, -16], [-8, 18]]
            if role == "ranger"
            else [[20, -16], [28, 8], [8, 16], [24, -4]]
        )
        self.reported = set()

    def move_to_target(self):
        if self.target_position[0:2] == [0.0, 0.0]:
            self.target_position[0:2] = self.waypoints[0]
        if all(
            abs(a - b) < self.TARGET_PRECISION
            for a, b in zip(self.target_position, self.current_pose[0:2])
        ):
            self.target_index = (self.target_index + 1) % len(self.waypoints)
            self.target_position[0:2] = self.waypoints[self.target_index]
            print(f"[{self.role}] next waypoint {self.target_position[0:2]}")
        desired = math.atan2(
            self.target_position[1] - self.current_pose[1],
            self.target_position[0] - self.current_pose[0],
        )
        angle_left = desired - self.current_pose[5]
        angle_left = (angle_left + 2 * math.pi) % (2 * math.pi)
        if angle_left > math.pi:
            angle_left -= 2 * math.pi
        yaw = self.MAX_YAW_DISTURBANCE * angle_left / (2 * math.pi)
        pitch = clamp(math.log10(abs(angle_left) + 1e-6), self.MAX_PITCH_DISTURBANCE, 0.1)
        return yaw, pitch

    def scan_fires(self):
        x, y, alt = self.current_pose[0], self.current_pose[1], self.current_pose[2]
        if alt < 8:
            return
        seen = set()
        if self.camera.hasRecognition():
            for obj in self.camera.getRecognitionObjects():
                model = obj.getModel()
                if model:
                    seen.add(model)
        for name, (fx, fy, temp_c, smoke) in FIRE_SITES.items():
            dist = math.hypot(x - fx, y - fy)
            visible = name in seen or dist < 28.0
            if not visible:
                continue
            # Farther detections are cooler (partial plume); close passes are hotter.
            brightness = temp_c * clamp(1.15 - dist / 80.0, 0.55, 1.1)
            level, reason = fire_level(brightness, smoke)
            key = (name, level)
            if level == "none" or key in self.reported:
                continue
            self.reported.add(key)
            print(
                f"[RANGER ONLY] fire_alert drone={self.getName()} role={self.role} "
                f"site={name} level={level} x={fx:.1f} y={fy:.1f} "
                f"brightness_c={brightness:.0f} reason={reason}"
            )

    def run(self):
        t1 = self.getTime()
        print(f"[{self.role}] OFF TOUR patrol armed, altitude {self.target_altitude} m")
        while self.step(self.time_step) != -1:
            roll, pitch, yaw = self.imu.getRollPitchYaw()
            x_pos, y_pos, altitude = self.gps.getValues()
            roll_acc, pitch_acc, _ = self.gyro.getValues()
            self.current_pose = [x_pos, y_pos, altitude, roll, pitch, yaw]
            yaw_disturbance = 0.0
            pitch_disturbance = 0.0
            if altitude > self.target_altitude - 1 and self.getTime() - t1 > 0.1:
                yaw_disturbance, pitch_disturbance = self.move_to_target()
                t1 = self.getTime()
                self.scan_fires()
            roll_input = self.K_ROLL_P * clamp(roll, -1, 1) + roll_acc
            pitch_input = self.K_PITCH_P * clamp(pitch, -1, 1) + pitch_acc + pitch_disturbance
            yaw_input = yaw_disturbance
            clamped_alt = clamp(
                self.target_altitude - altitude + self.K_VERTICAL_OFFSET, -1, 1
            )
            vertical_input = self.K_VERTICAL_P * pow(clamped_alt, 3.0)
            self.front_left_motor.setVelocity(
                self.K_VERTICAL_THRUST + vertical_input - yaw_input + pitch_input - roll_input
            )
            self.front_right_motor.setVelocity(
                -(self.K_VERTICAL_THRUST + vertical_input + yaw_input + pitch_input + roll_input)
            )
            self.rear_left_motor.setVelocity(
                -(self.K_VERTICAL_THRUST + vertical_input + yaw_input - pitch_input - roll_input)
            )
            self.rear_right_motor.setVelocity(
                self.K_VERTICAL_THRUST + vertical_input - yaw_input - pitch_input + roll_input
            )


if __name__ == "__main__":
    role = "ranger"
    if len(sys.argv) > 1 and sys.argv[1] in ("ranger", "thermal"):
        role = sys.argv[1]
    RangerEye(role).run()
