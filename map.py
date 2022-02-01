import pygame as p
import sys
import os
import json
import requests

p.init()


class Map:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 600, 450
        self.FPS = 30
        self.ZOOM_DELTA = 0.001
        self.WASD_DELTA_CONST = 0.714
        self.WASD_DELTA = 0

        self.window = p.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = p.time.Clock()

        self.url = 'https://static-maps.yandex.ru/1.x/'
        self.params = {'ll': '136.944448;28.819334',
                       'spn': '0.010.01',
                       'l': 'sat',
                       'z': '1'}
        self.ll = [37.530887, 55.703118]
        self.spn = [0.002, 0.002]
        self.l = 'map'
        self.z = 1
        self.map_img = self.get_map()

    def main_loop(self):
        run = True
        while run:
            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    sys.exit()

                if event.type == p.KEYDOWN:
                    if event.key == p.K_ESCAPE:
                        p.quit()
                        sys.exit()

                    if event.key == p.K_m and self.l != 'map':
                        self.l = 'map'
                    elif event.key == p.K_c and self.l != 'sat':
                        self.l = 'sat'
                    elif event.key == p.K_z and self.l != 'skl':
                        self.l = 'skl'


                    if event.key == p.K_PAGEUP:
                        self.spn[0] += self.ZOOM_DELTA
                        self.spn[1] += self.ZOOM_DELTA
                    elif event.key == p.K_PAGEDOWN:
                        self.spn[0] -= self.ZOOM_DELTA
                        self.spn[1] -= self.ZOOM_DELTA

                    if event.key == p.K_EQUALS:
                        self.spn[0] += self.ZOOM_DELTA * 10
                        self.spn[1] += self.ZOOM_DELTA * 10
                    elif event.key == p.K_MINUS:
                        self.spn[0] -= self.ZOOM_DELTA * 10
                        self.spn[1] -= self.ZOOM_DELTA * 10
                    self.spn[0] = max(self.spn[0], 0.001)
                    self.spn[1] = max(self.spn[1], 0.001)

                    self.WASD_DELTA = self.WASD_DELTA_CONST * self.spn[0]

                    if event.key == p.K_w:
                        self.ll[1] += self.WASD_DELTA * 0.9
                    if event.key == p.K_s:
                        self.ll[1] -= self.WASD_DELTA * 0.9
                    if event.key == p.K_a:
                        self.ll[0] -= self.WASD_DELTA
                    if event.key == p.K_d:
                        self.ll[0] += self.WASD_DELTA

                    self.map_img = self.get_map()
                    print(self.spn)
            self.window.blit(self.map_img, (0, 0))
            p.display.flip()
            self.clock.tick(self.FPS)

    def get_map(self):
        res = requests.get(self.get_url())
        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(res.content)

        return p.image.load(map_file)

    def get_url(self):
        return f'{self.url}?ll={self.ll[0]},{self.ll[1]}&spn={self.spn[0]},{self.spn[1]}&l={self.l}&z={self.z}'




map_prog = Map()
map_prog.main_loop()