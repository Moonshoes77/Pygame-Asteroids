import pygame
from pygame import Vector2
from player import Player
from asteroid import Asteroid
from random import randint
from timer import Timer
from collections.abc import Callable
import webbrowser

class Game:

    TICK_RATE = 60

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Roids")
        self._window = pygame.display.set_mode((1024, 768))
        self._clock = pygame.time.Clock()
        self._counter = 0
        self._score = 0
        self._level = 1
        self._new_game = False
        self._I_FRAMES = False
        self._game_over = False
        self._player_is_dead = True
        self._asteroids = []
        self._timers = []
        self._events = []
        self._bullets = []
        self._lives = [Player(self._window, self._bullets) for i in range(3)]
        self._player: Player | None = None
        self._add_timer(self._spawn_player, 4)
        self._populate_roids(self._level)
        pygame.display.set_icon(self._lives[0].mask.to_surface(pygame.Surface((32, 32))))
        

    def _populate_roids(self, current_level: int) -> None:
        for i in range(0, current_level + 1):
            pos_x = randint(0, self._window.get_width())
            pos_y = randint(0, self._window.get_height())
            self._asteroids.append(Asteroid(self._window, Vector2(pos_x, pos_y), Asteroid.SIZE.LARGE))


    def _kill_player(self) -> None:
        self._player = None
        self._lives.pop(0)
        if len(self._lives) == 0:
            self._game_over = True
        else:
            self._player_is_dead = True
            self._add_timer(self._spawn_player, 5)


    def _toggle_i_frames(self):
        self._I_FRAMES = not self._I_FRAMES


    def _spawn_player(self) -> None:
        self._player = self._lives[0]
        self._player_is_dead = False
        self._toggle_i_frames()
        self._add_timer(self._toggle_i_frames, 4)


    def _handle_events(self) -> None:
        self._events = [event for event in pygame.event.get()]
        for event in self._events:
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit()
                if event.key == pygame.K_g:
                    self._I_FRAMES = not self._I_FRAMES
                if event.key == pygame.K_F2 and self._game_over:
                    self._new_game = True
                if event.key == pygame.K_p:
                    print(self._bullets)
                    print(self._asteroids)
                if event.key == pygame.K_F1:
                    url = "https://github.com/Moonshoes77/Pygame-Asteroids"
                    webbrowser.open(url, new=0, autoraise=True)
                
    
    def _check_collisions(self) -> None:
        for asteroid in self._asteroids:
            if not self._I_FRAMES and not self._player is None:
                if self._player.collide(asteroid):
                    self._kill_player()
                    asteroid.take_damage(self._asteroids)
                    self._asteroids.remove(asteroid)
            for bullet in self._bullets:
                if bullet.collide(asteroid):
                    bullet.is_alive = False
                    asteroid.take_damage(self._asteroids)
                    self._asteroids.remove(asteroid)
                    self._score += asteroid.award_points()


    def _update_entities(self) -> None:
        if not self._player_is_dead:
            self._player.update(self._events)
            if self._I_FRAMES:
                if self._counter % 20 > 10:
                    self._player.display()
            else:    
                self._player.display()

        for asteroid in self._asteroids:
            asteroid.update()
            asteroid.display()
        
        for bullet in self._bullets:
            if bullet.is_alive:
                bullet.update()
                bullet.display(self._window)
        
        self._counter += 1
        if self._counter > 1000:
            self._counter = 0

    
    def _update_timers(self) -> None:
        for timer in self._timers:
            timer.tick()


    def _add_timer(self, function: Callable, seconds: int, *args, **kwargs) -> None:
        self._timers.append(Timer(function, seconds, self.TICK_RATE, *args, **kwargs))

    
    def _cleanup(self) -> None:
        ### use slice assignment on bullet and asteroid lists to maintain the reference in the entity classes
        self._bullets[:] = [bullet for bullet in self._bullets if bullet.is_alive]
        self._asteroids[:] = [asteroid for asteroid in self._asteroids if asteroid.is_alive]
        self._timers = [timer for timer in self._timers if timer.remaining > 0]


    def run(self) -> int:
        while True:
            if not self._game_over:
                self._window.fill(0)
                self._handle_events()
                self._update_entities()
                self._check_collisions()           
                self._update_timers()
                self._cleanup()
            else:
                self._window.fill(0)
                self._handle_events()
                if self._new_game:
                    break

            pygame.display.flip()
            pygame.display.set_caption(f"Roids | {self._clock.get_fps()} fps | score: {self._score}")
            self._clock.tick(self.TICK_RATE)

        return 1 if self._new_game else 0
