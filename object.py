import pygame as pg
import numpy as np
from constants import *

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
            self.angles[0] += x
            self.angles[1] += y
            self.angles[2] += z

            Rx = np.array([
                [1, 0, 0],
                [0, np.cos(self.angles[0]), -np.sin(self.angles[0])],
                [0, np.sin(self.angles[0]), np.cos(self.angles[0])]
            ])
            Ry = np.array([
                [np.cos(self.angles[1]), 0, np.sin(self.angles[1])],
                [0, 1, 0],
                [-np.sin(self.angles[1]), 0, np.cos(self.angles[1])]
            ])
            Rz = np.array([
                [np.cos(self.angles[2]), -np.sin(self.angles[2]), 0],
                [np.sin(self.angles[2]), np.cos(self.angles[2]), 0],
                [0, 0, 1]
            ])

            self.vertices = np.dot(self.base_vertices, Rx)
            self.vertices = np.dot(self.vertices, Ry)
            self.vertices = np.dot(self.vertices, Rz)

