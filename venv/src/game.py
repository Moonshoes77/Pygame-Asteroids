import pygame
from pygame import Vector2
from player import Player
from asteroid import Asteroid
from random import randint
from timer import Timer
from collections.abc import Callable


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Roids")
        self._window = pygame.display.set_mode((1024, 768))
        self._clock = pygame.time.Clock()
        self._lives = [Player(self._window) for i in range(3)]
        self._player = self._lives[0]
        self._level = 1
        self._roids = []
        self._game_over = False
        self._populate_roids(self._level)
        self._timers = []


    def _populate_roids(self, current_level: int):
        for i in range(0, current_level + 1):
            pos_x = randint(0, self._window.get_width())
            pos_y = randint(0, self._window.get_height())
            self._roids.append(Asteroid(self._window, Vector2(pos_x, pos_y), Asteroid.SIZE.LARGE))


    def _kill_player(self):
        self._lives.pop(0)
        if len(self._lives) == 0:
            self._game_over = True
        else:
            self._player = self._lives[0]    

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit()
                if event.key == pygame.K_r: ### reset / debug info
                    self._roids = []
                    self._level = 1
                    self._populate_roids(self._level)
                    print(f"timers: {self._timers}")


    def _update_entities(self):
        self._player.update()
        self._player.display()
        for asteroid in self._roids:
            asteroid.update()
            asteroid.display()
            if self._player.collide(asteroid):
                self._kill_player()

    
    def _update_timers(self):
        expired_timers = [timer for timer in self._timers if timer.remaining == 0]
        for timer in self._timers:
            timer.tick()
        for timer in expired_timers:
            self._remove_timer(timer)
    
    def _add_timer(self, function: Callable, seconds: int, *args, **kwargs) -> None:
        self._timers.append(Timer(function, seconds, *args, **kwargs))


    def _remove_timer(self, timer: Timer) -> None:
        index = self._timers.index(timer)
        self._timers.pop(index)


    def run(self) -> None:
        while not self._game_over:
            self._window.fill(0)
            self._handle_events()
            self._update_entities()            
            self._update_timers()
            pygame.display.flip()
            self._clock.tick(60)