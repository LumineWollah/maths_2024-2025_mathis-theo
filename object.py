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
    
    def world_to_camera(self, point, camera):
        cos_yaw = math.cos(-camera.yaw)
        sin_yaw = math.sin(-camera.yaw)
        cos_pitch = math.cos(-camera.pitch)
        sin_pitch = math.sin(-camera.pitch)

        rotation_yaw = np.array([
            [cos_yaw, 0, sin_yaw],
            [0, 1, 0],
            [-sin_yaw, 0, cos_yaw]
        ])

        rotation_pitch = np.array([
            [1, 0, 0],
            [0, cos_pitch, -sin_pitch],
            [0, sin_pitch, cos_pitch]
        ])

        rotation_matrix = rotation_pitch @ rotation_yaw

        translated_point = point - camera.position
        camera_point = rotation_matrix @ translated_point
        return camera_point

    def draw(self, surface, fov, distance, camera):
        transformed_vertices = []
        for v in self.vertices:
            camera_space_vertex = self.world_to_camera(v, camera)
            projected_point = self.project(camera_space_vertex, fov, distance)
            transformed_vertices.append(projected_point)

        for edge in self.edges:
            pg.draw.line(surface, (255, 255, 255), transformed_vertices[edge[0]], transformed_vertices[edge[1]], 2)

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
        self.angles[0] = x
        self.angles[1] = y
        self.angles[2] = z

        qx = Quaternion(math.cos(x/2), math.sin(x/2), 0, 0)
        qy = Quaternion(math.cos(y/2), 0, math.sin(y/2), 0)
        qz = Quaternion(math.cos(z/2), 0, 0, math.sin(z/2))

        q_total = qz * qy * qx

        rotated_vertices = []
        for v in self.base_vertices:
            rotated_v = q_total.rotate_vector(v)
            rotated_vertices.append(rotated_v)

        self.vertices = np.array(rotated_vertices)

    def rotateRelativeWithMatrix(self, dx=0, dy=0, dz=0):
        self.rotateWithMatrix(self.angles[0]+dx, self.angles[1]+dy, self.angles[2]+dz)
    
    def rotateRelativeWithQuaternions(self, dx=0, dy=0, dz=0):
        self.rotateWithQuaternions(self.angles[0]+dx, self.angles[1]+dy, self.angles[2]+dz)

class Tetrahedron(Object):
    def __init__(self):
        vertices = np.array([
            [1, 1, 1],
            [-1, -1, 1],
            [-1, 1, -1],
            [1, -1, -1]
        ])

        edges = [
            (0, 1), (0, 2), (0, 3),
            (1, 2), (1, 3), (2, 3)
        ]

        super().__init__(
            positions=[0, 0, 0],
            angles=[0, 0, 0],
            vertices=vertices,
            edges=edges
        )

class Cube(Object):
    def __init__(self):
        super().__init__(
            positions = [0, 0, 0],
            angles = [0, 0, 0],
            vertices = np.array([
                [-1, -1, -1],
                [1, -1, -1],
                [1, 1, -1],
                [-1, 1, -1],
                [-1, -1, 1],
                [1, -1, 1],
                [1, 1, 1],
                [-1, 1, 1]
            ]),
            edges = [
                (0, 1), (1, 2), (2, 3), (3, 0),
                (4, 5), (5, 6), (6, 7), (7, 4),
                (0, 4), (1, 5), (2, 6), (3, 7)
            ]
        )

class Pyramid(Object):
    def __init__(self):
        vertices = np.array([
            [-1, -1, -1],
            [1, -1, -1],
            [1, -1, 1],
            [-1, -1, 1],
            [0, 1, 0]
        ])

        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (0, 4), (1, 4), (2, 4), (3, 4)
        ]

        super().__init__(
            positions=[0, 0, 0],
            angles=[0, 0, 0],
            vertices=vertices,
            edges=edges
        )

class Sphere(Object):
    def __init__(self, detail=10):
        vertices = []
        edges = []

        for i in range(detail + 1):
            theta = np.pi * i / detail
            for j in range(detail):
                phi = 2 * np.pi * j / detail
                x = np.sin(theta) * np.cos(phi)
                y = np.cos(theta)
                z = np.sin(theta) * np.sin(phi)
                vertices.append([x, y, z])

        for i in range(detail):
            for j in range(detail):
                current = i * detail + j
                next_j = (j + 1) % detail
                next_i = i + 1

                if next_i <= detail:
                    right = i * detail + next_j
                    down = next_i * detail + j
                    down_right = next_i * detail + next_j

                    edges.append((current, right))
                    edges.append((current, down))
                    edges.append((current, down_right))

        super().__init__(
            positions=[0, 0, 0],
            angles=[0, 0, 0],
            vertices=np.array(vertices),
            edges=edges
        )

     