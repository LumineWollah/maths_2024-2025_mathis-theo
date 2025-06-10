import numpy as np
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

from keymap import keymap

class Camera:
    def __init__(self):
        self.pos = np.array([0, 0, 5], dtype=np.float32)
        self.pitch = 0.0
        self.yaw = 0.0
        self.mouse_sensitivity = 0.15
        self.speed = 5.0

    def process_mouse_motion(self, dx, dy):
        self.yaw += dx * self.mouse_sensitivity
        self.pitch -= dy * self.mouse_sensitivity  # inversion volontaire pour effet naturel

        # Clamp pitch entre -89 et 89 pour éviter gimbal lock
        self.pitch = max(-89, min(89, self.pitch))

    def get_direction_vectors(self):
        pitch_rad = np.radians(self.pitch)
        yaw_rad = np.radians(self.yaw)

        forward = np.array([
            np.cos(pitch_rad) * np.sin(yaw_rad),
            np.sin(pitch_rad),
            -np.cos(pitch_rad) * np.cos(yaw_rad)
        ], dtype=np.float32)
        forward /= np.linalg.norm(forward)

        up_global = np.array([0,1,0], dtype=np.float32)
        right = np.cross(forward, up_global)
        right /= np.linalg.norm(right)

        up = np.cross(right, forward)
        up /= np.linalg.norm(up)

        return forward, right, up

    def update_position(self, keys, dt):
        forward, right, up = self.get_direction_vectors()
        velocity = self.speed * dt

        if keys[keymap["forward"]]:
            self.pos += forward * velocity
        if keys[keymap["backward"]]:
            self.pos -= forward * velocity
        if keys[keymap["right"]]:
            self.pos += right * velocity
        if keys[keymap["left"]]:
            self.pos -= right * velocity
        if keys[keymap["up"]]:
            self.pos += up * velocity
        if keys[keymap["down"]]:
            self.pos -= up * velocity

    def apply_view(self):
        forward, right, up = self.get_direction_vectors()
        center = self.pos + forward
        # gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, up_x, up_y, up_z)
        gluLookAt(
            self.pos[0], self.pos[1], self.pos[2],
            center[0], center[1], center[2],
            up[0], up[1], up[2]
        )
