import pygame
from pygame import Vector2
from player import Player
from asteroid import Asteroid
from random import randint
from timer import Timer
from collections.abc import Callable

god_mode = True

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
        self._events = []
        pygame.display.set_icon(self._player.mask.to_surface(pygame.Surface((32, 32))))

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
        self._events = [event for event in pygame.event.get()]
        
        for event in self._events:
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit()


    def _update_entities(self):
        self._player.update(self._events)
        self._player.display()
        for asteroid in self._roids:
            asteroid.update()
            asteroid.display()
            if self._player.collide(asteroid):
                if not god_mode:
                    self._kill_player()

    
    def _update_timers(self):
        expired_timers = [timer for timer in self._timers if timer.remaining == 0]
        for timer in self._timers:
            timer.tick()
        for timer in expired_timers:
            self._timers.remove(timer)


    def _add_timer(self, function: Callable, seconds: int, *args, **kwargs) -> None:
        self._timers.append(Timer(function, seconds, *args, **kwargs))


    def run(self) -> None:
        while not self._game_over:
            self._window.fill(0)
            self._handle_events()
            self._update_entities()            
            self._update_timers()
            pygame.display.flip()
            self._clock.tick(60)
            pygame.display.set_caption(f"Roids | {self._clock.get_fps()} fps")
