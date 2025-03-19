import math
import random

class Quaternion:
    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Quaternion(
            self.w + other.w,
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )
    
    def __sub__(self, other):
        return Quaternion(
            self.w - other.w,
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )
    
    def __mul__(self, other):
        if isinstance(other, Quaternion):
            w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
            x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
            y = self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x
            z = self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
            return Quaternion(w, x, y, z)
        elif isinstance(other, (int, float)):
            return Quaternion(self.w * other, self.x * other, self.y * other, self.z * other)
    
    def conjugate(self):
        return Quaternion(self.w, -self.x, -self.y, -self.z)
    
    def norm(self):
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        n = self.norm()
        if n == 0:
            return Quaternion(1, 0, 0, 0)
        return Quaternion(self.w / n, self.x / n, self.y / n, self.z / n)
    
    def rotate_vector(self, vector):
        q_vec = Quaternion(0, *vector)
        rotated_vec = self * q_vec * self.conjugate()
        return (rotated_vec.x, rotated_vec.y, rotated_vec.z)
    
    def to_rotation_matrix(self):
        w, x, y, z = self.w, self.x, self.y, self.z
        return [
            [1 - 2*y*y - 2*z*z, 2*x*y - 2*w*z, 2*x*z + 2*w*y],
            [2*x*y + 2*w*z, 1 - 2*x*x - 2*z*z, 2*y*z - 2*w*x],
            [2*x*z - 2*w*y, 2*y*z + 2*w*x, 1 - 2*x*x - 2*y*y]
        ]
    @staticmethod
    def random():
        return Quaternion(
            random.uniform(-1, 1),
            random.uniform(-1, 1),
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        ).normalize()
    
    def __repr__(self):
        return f"Quaternion({self.w}, {self.x}, {self.y}, {self.z})"
