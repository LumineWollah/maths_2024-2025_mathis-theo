import pygame as pg
import numpy as np

SCREEN_SIZE = (800, 600)
# FOV_V = np.pi / 4
# FOV_H = FOV_V * SCREEN_SIZE[0] / SCREEN_SIZE [1]

class Engine():
    def __init__(self):
        pg.init()
        self.running = True
        self.screen_size = SCREEN_SIZE
        self.screen = pg.display.set_mode(self.screen_size)
        self.clock = pg.time.Clock()
        self.surf = pg.surface.Surface(SCREEN_SIZE)
        self.bg = (0, 0, 0)

        # self.points = np.asarray([[1, 1, 1, 1, 1], [4, 2, 0, 1, 1], [1, .5, 3, 1, 1]])
        # self.triangles = np.asarray([[0, 1, 2]])
        self.camera = np.asarray([13, 0.5, 2, 3.3, 0])
        self.cube_vertices = np.array([
            [-1, -1, -1],
            [1, -1, -1],
            [1, 1, -1],
            [-1, 1, -1],
            [-1, -1, 1],
            [1, -1, 1],
            [1, 1, 1],
            [-1, 1, 1]
        ])
        self.cube_edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        self.cube_angles = [0, 0, 0]

    def run(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT: self.running = False
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: self.running = False

            Rx = np.array([
                [1, 0, 0],
                [0, np.cos(self.cube_angles[0]), -np.sin(self.cube_angles[0])],
                [0, np.sin(self.cube_angles[0]), np.cos(self.cube_angles[0])]
            ])
            Ry = np.array([
                [np.cos(self.cube_angles[1]), 0, np.sin(self.cube_angles[1])],
                [0, 1, 0],
                [-np.sin(self.cube_angles[1]), 0, np.cos(self.cube_angles[1])]
            ])
            Rz = np.array([
                [np.cos(self.cube_angles[2]), -np.sin(self.cube_angles[2]), 0],
                [np.sin(self.cube_angles[2]), np.cos(self.cube_angles[2]), 0],
                [0, 0, 1]
            ])
            rotated_vertices = np.dot(self.cube_vertices, Rx)
            rotated_vertices = np.dot(rotated_vertices, Ry)
            rotated_vertices = np.dot(rotated_vertices, Rz)

            projected_points = [self.project(v, fov=3, distance=5) for v in rotated_vertices]

            self.screen.fill(self.bg)

            for edge in self.cube_edges:
                pg.draw.line(self.screen, (255, 255, 255), projected_points[edge[0]], projected_points[edge[1]], 2)

            self.cube_angles[0] += 0.02
            self.cube_angles[1] += 0.01
            self.cube_angles[2] += 0.015

            pg.display.update()
            self.clock.tick(60)

    def project(self, point, fov, distance):
        factor = fov / (distance + point[2])
        x = int(self.screen_size[0] / 2 + point[0] * factor * self.screen_size[0] / 2)
        y = int(self.screen_size[1] / 2 - point[1] * factor * self.screen_size[1] / 2)
        return (x, y)
    
engine = Engine()
engine.run()
