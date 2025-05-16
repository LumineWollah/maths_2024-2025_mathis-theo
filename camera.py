import numpy as np
import math

class Camera:
    def __init__(self, position=np.array([0.0, 0.0, 0.0]), yaw=0.0, pitch=0.0):
        self.position = position
        self.yaw = yaw
        self.pitch = pitch

    def get_direction(self):
        x = math.cos(self.pitch) * math.sin(self.yaw)
        y = math.sin(self.pitch)
        z = math.cos(self.pitch) * math.cos(self.yaw)
        return np.array([x, y, z])

    def move(self, direction, amount):
        self.position += direction * amount

    def rotate(self, delta_yaw, delta_pitch):
        self.yaw += delta_yaw
        self.pitch += delta_pitch
        max_pitch = math.radians(89.0)
        self.pitch = max(-max_pitch, min(max_pitch, self.pitch))