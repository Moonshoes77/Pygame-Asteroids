import pygame
from pygame import Vector2
from player import Player
from asteroid import Asteroid
from random import randint
from timer import Timer
from collections.abc import Callable
from enum import Enum
import webbrowser


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
        self._state = self.STATE.WAIT
        self._score = 0
        self._level = 1
        self._asteroids = []
        self._timers = []
        self._events = []
        self._bullets = []
        self._lives = [Player(self._window, self._bullets) for i in range(3)]
        self._player: Player | None = None
        self._menu = MainMenu(self._window, self)
        self._scoreboard = TitleCard(self._window, f"Score: {self._score: 10} {" ":10} Lives: {len(self._lives)}", TitleCard.SIZE.SMALL, (Vector2(self._window.get_width() - (self._window.get_width() / 4), 30)))
        self._game_over_card = TitleCard(self._window, "GAME OVER", TitleCard.SIZE.LARGE, Vector2(self._window.get_rect().center))
        self._new_game_card = TitleCard(self._window, "'F2' for new game or 'q' to quit", TitleCard.SIZE.SMALL, 
                                        Vector2(self._window.get_rect().center[0], self._window.get_rect().center[1] + 60))
        pygame.display.set_icon(self._lives[0].mask.to_surface(pygame.Surface((32, 32))))
   

    @property
    def events(self):
        return self._events

    @property
    def scene(self):
        return self.scene
    
    @scene.setter
    def scene(self, scene: "Game.SCENE"):
        self._scene = scene

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state: "Game.STATE"):
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


    def _enable_i_frames(self) -> None:
        if self._player is not None:
            self._player.set_invulnerable()


    def _disable_i_frames(self) -> None:
        if self._player is not None:
            self._player.set_vulnerable()


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
        self._events[:] = [event for event in pygame.event.get()]
        for event in self._events:
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit()
                if event.key == pygame.K_g:
                    if self._player is not None:
                        if self._player.state == Player.STATE.INVULNERABLE:
                            self._player.set_vulnerable()
                        elif self._player.state == Player.STATE.VULNERABLE:
                            self._player.set_invulnerable()

                if event.key == pygame.K_F2:
                    self._state = self.STATE.NEW_GAME
                if event.key == pygame.K_F3:
                    self._scene = self.SCENE.GAME
                if event.key == pygame.K_p:
                    print(self._bullets)
                    print(self._asteroids)

                     
    def _check_collisions(self) -> None:
        for asteroid in self._asteroids:
            if (self._state == self.STATE.PLAYING 
                and self._player is not None
                and self._player.state != Player.STATE.INVULNERABLE):
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
            self._player.display()

        for asteroid in self._asteroids:
            asteroid.update()
            asteroid.display()
        
        for bullet in self._bullets:
            if bullet.is_alive:
                bullet.update()
                bullet.display(self._window)       


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
        # pygame.display.set_caption(f"Roids | {self._clock.get_fps()} fps | score: {self._score} | State: {self._state} | Scene: {self._scene}")
        self._clock.tick_busy_loop(self.TICK_RATE)


    def _level_transition(self) -> None:
        self._populate_asteroids(self._level)
        if self._player is None:
            self._spawn_player()
        else:
            self._enable_i_frames()
            self._add_timer(self._disable_i_frames, 4)
        self._state = self.STATE.PLAYING


    def _update(self) -> None:
        self._window.fill(0)
        self._handle_events()
        self._update_entities()
        self._check_collisions()           
        self._update_timers()
        
        match self._state:
            case self.STATE.NEW_GAME:
                self._new_game()
            case self.STATE.PLAYING:
                self._check_level_clear()
            case self.STATE.LEVEL_TRANSITION:
                self._level_transition()
            case self.STATE.GAME_OVER:
                self._game_over_card.display()
                self._new_game_card.display()
            case self.STATE.WAIT:
                pass
        self._scoreboard.update(f"Score: {self._score: 10} {" ":10} Lives: {len(self._lives)}")
        self._cleanup()


    def run(self) -> None:
        while True:
            match self._scene:
                case self.SCENE.MAIN_MENU:
                    self._update()
                    self._menu.display()
                case self.SCENE.GAME:
                    self._update()
                    self._scoreboard.display()

            self._advance_frame() 
                

class Button:

    pygame.font.init()
    FONT = pygame.font.SysFont("Arial", 18)
    STATE = Enum("state", ["WAITING", "CLICKED"])

    def __init__(self, window: pygame.Surface,  pos: Vector2, width: int, height: int, function: Callable | None, text: str | None = None):
        self._pos = pos
        self.rect = pygame.Rect(self._pos, (width, height))
        self._text = text
        self._window_ref = window
        self._function = function
        self._state = self.STATE.WAITING


    def display(self):
        surf = pygame.Surface(self.rect.size)
        text = self.FONT.render(self._text, True, (255, 255, 255))
        surf.fill((127, 127, 127))
        surf.blit(text, ((surf.get_width() // 2) - (text.get_width() // 2), (surf.get_height() // 2) - (text.get_height() // 2)))
        self._window_ref.blit(surf, self._pos)


    def check_clicked(self, events: list):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self._state = self.STATE.CLICKED
                    self.on_click()
                    self._state = self.STATE.WAITING


    def on_click(self):
        if self._function is not None and self._state == self.STATE.CLICKED:
            return self._function()



class TitleCard:

    SIZE = Enum('size', [("MEDIUM", 72), ("LARGE", 100), ("SMALL", 40)])
    COLOR = (255, 255, 255)

    def __init__(self, window: pygame.Surface, text: str, size: "TitleCard.SIZE", pos: Vector2) -> None:
        self._font = pygame.font.SysFont("Arial", size.value)
        self._text = text
        self._text_render = self._font.render(self._text, True, self.COLOR)
        self._pos = pos
        self._window_ref = window


    def update(self, text: str) -> None:
        self._text = text
        self._text_render = self._font.render(self._text, True, self.COLOR)


    def display(self) -> None:
        self._window_ref.blit(self._text_render, ((self._pos.x) - (self._text_render.get_width() // 2), 
                                                 (self._pos.y) - (self._text_render.get_height() // 2)))
            


class MainMenu:

    STATE = Enum("state", ["BUTTON_CLICKED", "WAITING"])

    def __init__(self, window: pygame.Surface, parent: Game) -> None:
        self._title_card = TitleCard(window, "Roids!", TitleCard.SIZE.LARGE, Vector2(window.get_rect().center))
        self._window_ref = window
        self._parent = parent
        self._w_width = window.get_width()
        self._w_height = window.get_height()
        self._github_button = Button(window, Vector2((self._w_width // 2) - 250, self._w_height - 300), 
                                                     175, 100, self._open_github, "See on github!")
        self._play_button = Button(window, Vector2((self._w_width // 2) + 50, self._w_height - 300),
                                                   175, 100, self._start_game, "Play")
        self._buttons = [self._github_button, self._play_button]


    def _open_github(self) -> None:
        url = "https://github.com/Moonshoes77/Pygame-Asteroids"
        webbrowser.open(url, new=0, autoraise=True)


    def _start_game(self) -> None:
        self._parent.scene = self._parent.SCENE.GAME
        self._parent.state = self._parent.STATE.NEW_GAME


    def display(self) -> None:
        self._title_card.display()
        for button in self._buttons:
            button.display()
            button.check_clicked(self._parent.events)
