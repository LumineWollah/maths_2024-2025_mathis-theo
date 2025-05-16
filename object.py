import pygame as pg
import numpy as np
import math
from constants import *
from quaternion import Quaternion

class Object:

    def __init__(self, positions, angles, vertices, edges):
        self.positions = positions
        self.angles = angles
        self.base_vertices = vertices
        self.vertices = vertices
        self.edges = edges

    def project(self, point, fov, distance):
        factor = fov / (distance + point[2])
        x = int(SCREEN_SIZE[0] / 2 + point[0] * factor * SCREEN_SIZE[0] / 2)
        y = int(SCREEN_SIZE[1] / 2 - point[1] * factor * SCREEN_SIZE[1] / 2)
        return (x, y)

    def draw(self, surface, fov, distance):
        projected_points = [self.project(v, fov=fov, distance=distance) for v in self.vertices]
        for edge in self.edges:
            pg.draw.line(surface, (255, 255, 255), projected_points[edge[0]], projected_points[edge[1]], 2)

    def rotateWithMatrix(self, x=0, y=0, z=0):
        # Mise à jour des angles d'Euler
        self.angles[0] = x
        self.angles[1] = y
        self.angles[2] = z

        # Matrices de rotation pour chaque axe
        Rx = np.array([
            [1, 0, 0],
            [0, math.cos(x), -math.sin(x)],
            [0, math.sin(x), math.cos(x)]
        ])
        Ry = np.array([
            [math.cos(y), 0, math.sin(y)],
            [0, 1, 0],
            [-math.sin(y), 0, math.cos(y)]
        ])
        Rz = np.array([
            [math.cos(z), -math.sin(z), 0],
            [math.sin(z), math.cos(z), 0],
            [0, 0, 1]
        ])

        # Matrice de rotation combinée : R = Rz * Ry * Rx
        R = Rz @ Ry @ Rx

        # Application de la rotation aux sommets de base
        self.vertices = np.dot(self.base_vertices, R.T)

    def rotateWithQuaternions(self, x=0, y=0, z=0):
        self.angles[0] += x
        self.angles[1] += y
        self.angles[2] += z

        qx = Quaternion(math.cos(x/2), math.sin(x/2), 0, 0)
        qy = Quaternion(math.cos(y/2), 0, math.sin(y/2), 0)
        qz = Quaternion(math.cos(z/2), 0, 0, math.sin(z/2))

        q_total = qz * qy * qx

        rotated_vertices = []
        for v in self.base_vertices:
            rotated_v = q_total.rotate_vector(v)
            rotated_vertices.append(rotated_v)

        self.vertices = np.array(rotated_vertices)
