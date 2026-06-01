import pygame
from pygame import Vector2
from player import Player
from asteroid import Asteroid
from random import randint

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Roids")
        self._window = pygame.display.set_mode((1024, 768))
        self._clock = pygame.time.Clock()
        self._lives = [Player(self._window) for i in range(3)]
        self._level = 1
        self._roids = []
        self._game_over = False
        self._populate_roids(self._level)

    def _populate_roids(self, current_level: int):
        for i in range(0, current_level + 1):
            pos_x = randint(0, self._window.get_width())
            pos_y = randint(0, self._window.get_height())
            self._roids.append(Asteroid(self._window, Vector2(pos_x, pos_y), Asteroid.SIZE.LARGE))
        

    
    def run(self) -> None:
        while not self._game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        quit()
                    if event.key == pygame.K_r:
                        self._roids = []
                        self._level = 1
                        self._populate_roids(self._level)
                        print(self._lives)
            
            self._window.fill(0)


            self._lives[0].update()
            self._lives[0].display()

            for asteroid in self._roids:
                asteroid.update()
                asteroid.display()
                if self._lives[0].collide(asteroid):
                    self._lives.pop(0)
                    if len(self._lives) == 0:
                        self._game_over = True
   


            # if self._roids == []:
            #     self._increase_level(self._level)
            pygame.display.flip()
            self._clock.tick(60)
    