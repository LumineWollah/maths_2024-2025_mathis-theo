import pygame as pg
import numpy as np
import math

from constants import *
from cube import Cube
from camera import Camera

FOV = 3
DISTANCE = 10

# FOV_V = np.pi / 4
# FOV_H = FOV_V * SCREEN_SIZE[0] / SCREEN_SIZE [1]

class Engine():
    def __init__(self):
        pg.init()
        self.running = True
        self.screen_size = SCREEN_SIZE
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.clock = pg.time.Clock()
        self.surf = pg.surface.Surface(SCREEN_SIZE)
        self.bg = (0, 0, 0)

        self.camera = Camera(position=np.array([0.0, 0.0, 5.0]))

        self.scene = [
            Cube(),
        ]

    def run(self):
        isMousePressed = False

        while self.running:
            self.screen.fill(self.bg)

            dt = self.clock.tick(60) / 1000
            
            # EVENT
            for event in pg.event.get():
                if event.type == pg.QUIT: self.running = False
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: self.running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        isMousePressed = True
                if event.type == pg.MOUSEBUTTONUP:
                    if event.button == 1:
                        isMousePressed = False

            # self.camera
            mouse_dx, mouse_dy = pg.mouse.get_rel()
            sensitivity = 0.005
            if isMousePressed:
                self.camera.rotate(-mouse_dx * sensitivity, -mouse_dy * sensitivity)

            keys = pg.key.get_pressed()
            move_speed = 5.0 * dt
            direction = self.camera.get_direction()
            right = np.cross(direction, np.array([0.0, 1.0, 0.0]))
            right /= np.linalg.norm(right)

            if keys[pg.K_w]:
                self.camera.move(direction, move_speed)
            if keys[pg.K_s]:
                self.camera.move(-direction, move_speed)
            if keys[pg.K_a]:
                self.camera.move(right, move_speed)
            if keys[pg.K_d]:
                self.camera.move(-right, move_speed)
            if keys[pg.K_SPACE]:
                self.camera.move(np.array([0.0, 1.0, 0.0]), move_speed)
            if keys[pg.K_LSHIFT]:
                self.camera.move(np.array([0.0, -1.0, 0.0]), move_speed)

            # SCENE
            for obj in self.scene:
                obj.rotateRelativeWithQuaternions(0, 0.01, 0)
                obj.draw(self.screen, FOV, DISTANCE, self.camera)

            pg.display.update()
            self.clock.tick(60)

engine = Engine()
engine.run()
