import pygame
from pygame import Vector2
from player import Player
from asteroid import Asteroid
from user_interface import *
from random import randint
from timer import Timer
from collections.abc import Callable
from enum import Enum


class Game:

    TICK_RATE = 60
    SCENE = Enum('scene', ["MAIN_MENU", "GAME"])
    STATE = Enum('state', ["NEW_GAME", "PLAYING", "LEVEL_TRANSITION", "RESPAWN", "GAME_OVER", "WAIT"])

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Roids")
        self._window = pygame.display.set_mode((1366, 768))
        self._clock = pygame.time.Clock()
        self._scene = self.SCENE.MAIN_MENU
        self._state = self.STATE.NEW_GAME
        self._counter = 0
        self._score = 0
        self._level = 1
        self._I_FRAMES = False
        self._asteroids = []
        self._timers = []
        self._events = []
        self._bullets = []
        self._lives = [Player(self._window, self._bullets) for i in range(3)]
        self._player: Player | None = None
        self._menu = MainMenu(self._window, self)
        pygame.display.set_icon(self._lives[0].mask.to_surface(pygame.Surface((32, 32))))

        
    @property
    def state(self) -> STATE:
        return self._state
    
    @state.setter
    def state(self, state: STATE):
        self._state = state
    

    def _populate_asteroids(self, current_level: int) -> None:
        for i in range(0, current_level + 1):
            pos_x = randint(0, self._window.get_width())
            pos_y = randint(0, self._window.get_height())
            self._asteroids.append(Asteroid(self._window, Vector2(pos_x, pos_y), Asteroid.SIZE.LARGE))


    def _kill_player(self) -> None:
        self._lives.pop(0)
        self._player = None
        if len(self._lives) == 0:
            self._state = self.STATE.GAME_OVER
        else:
            self._add_timer(self._spawn_player, 3)
            self._state = self.STATE.RESPAWN


    def _enable_i_frames(self):
        self._I_FRAMES = True


    def _disable_i_frames(self):
        self._I_FRAMES = False


    def _check_level_clear(self) -> None:
        if not self._state == self.STATE.PLAYING: ### Guard against setting timers every frame during transition
            return
        if len(self._asteroids) == 0:
                self._level += 1
                self._state = self.STATE.WAIT
                self._add_timer(self._set_state, 3, self.STATE.LEVEL_TRANSITION)


    def _set_state(self, state: "Game.STATE") -> None:
        self._state = state


    def _spawn_player(self) -> None:
        self._player = self._lives[0]
        self._enable_i_frames()
        self._add_timer(self._disable_i_frames, 4)
        self._state = self.STATE.PLAYING


    def _new_game(self) -> None:
        self._asteroids = []
        self._timers = []
        self._events = []
        self._bullets = []
        self._counter = 0
        self._score = 0
        self._level = 1
        self._lives = [Player(self._window, self._bullets) for i in range(3)]
        self._player: Player | None = None
        self._state = self.STATE.LEVEL_TRANSITION


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
                if event.key == pygame.K_F2 and self._state == self.STATE.GAME_OVER:
                    self._state = self.STATE.NEW_GAME
                if event.key == pygame.K_p:
                    print(self._bullets)
                    print(self._asteroids)
                    
                
    
    def _check_collisions(self) -> None:
        for asteroid in self._asteroids:
            if (self._state == self.STATE.PLAYING
                and not self._I_FRAMES
                and self._player is not None):
                    if self._player.collide(asteroid):
                        self._kill_player()
                        asteroid.take_damage(self._asteroids)
                        asteroid.is_alive = False
                        return
                    
            for bullet in self._bullets:
                if bullet.collide(asteroid):
                    bullet.is_alive = False
                    asteroid.take_damage(self._asteroids)
                    asteroid.is_alive = False
                    self._score += asteroid.award_points()


    def _update_entities(self) -> None:
        if self._player is not None:
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
        self._bullets[:] = [bullet for bullet in self._bullets if bullet.is_alive]
        self._asteroids[:] = [asteroid for asteroid in self._asteroids if asteroid.is_alive]
        self._timers = [timer for timer in self._timers if timer.remaining > 0]


    def _advance_frame(self) -> None:
        pygame.display.flip()
        pygame.display.set_caption(f"Roids | {self._clock.get_fps()} fps | score: {self._score} | State: {self._state}")
        self._clock.tick_busy_loop(self.TICK_RATE)

    def _PLAYING_run(self) -> None:
        self._window.fill(0)
        self._update_entities()
        self._check_collisions()           
        self._handle_events()
        self._update_timers()
        self._cleanup()
        self._check_level_clear()


    def _LEVEL_TRANSITION_RUN(self) -> None:
        self._populate_asteroids(self._level)
        if self._player is None:
            self._spawn_player()
        else:
            self._enable_i_frames()
            self._add_timer(self._disable_i_frames, 4)
        self._state = self.STATE.PLAYING

    
    def _GAME_OVER_run(self) -> None:
        self._window.fill(0)
        self._update_entities()
        self._handle_events()
        self._update_timers()
        self._cleanup()


    def _RESPAWN_run(self) -> None:
        self._window.fill(0)
        self._handle_events()
        self._update_entities()
        self._check_collisions()           
        self._update_timers()
        self._cleanup()

        
    def run(self) -> None:
        while True:
            match self._scene:
                case self.SCENE.MAIN_MENU:
                    self._menu.display()
                    self._handle_events()
                
                case self.SCENE.GAME:
                    match self._state:
                        case self.STATE.PLAYING:
                            self._PLAYING_run()   

                        case self.STATE.GAME_OVER:
                            self._GAME_OVER_run()

                        case self.STATE.NEW_GAME:
                            self._new_game()

                        case self.STATE.LEVEL_TRANSITION:
                            self._LEVEL_TRANSITION_RUN()
                        
                        case self.STATE.RESPAWN:
                            self._RESPAWN_run()

                        case self.STATE.WAIT:
                            self._PLAYING_run()

            self._advance_frame() 
                

