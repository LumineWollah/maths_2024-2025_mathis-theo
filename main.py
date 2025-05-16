import pygame as pg
import numpy as np

from cube import Cube
from constants import *

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

        self.camera = np.asarray([13, 0.5, 2, 3.3, 0])

        self.scene = [
            Cube(),
        ]

    def run(self):
        while self.running:
            self.screen.fill(self.bg)

            for event in pg.event.get():
                if event.type == pg.QUIT: self.running = False
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: self.running = False

            for obj in self.scene:
                obj.rotateWithMatrix(0.005, 0.01, 0.015)
                obj.draw(self.screen, FOV, DISTANCE)

            pg.display.update()
            self.clock.tick(60)

engine = Engine()
engine.run()
