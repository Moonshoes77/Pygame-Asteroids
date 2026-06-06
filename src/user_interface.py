import pygame
from pygame import Vector2
from collections.abc import Callable
from enum import Enum
import webbrowser



class Button:

    pygame.font.init()
    FONT = pygame.font.SysFont("Arial", 24)

    def __init__(self, window: pygame.Surface,  pos: Vector2, width: int, height: int, function: Callable | None, text: str | None = None):
        self._pos = pos
        self.rect = pygame.Rect(self._pos, (width, height))
        self._text = text
        self._window_ref = window
        self._function = function


    def display(self):
        surf = pygame.Surface(self.rect.size)
        text = self.FONT.render(self._text, True, (255, 255, 255))
        surf.fill((127, 127, 127))
        surf.blit(text, ((surf.get_width() // 2) - (text.get_width() // 2), (surf.get_height() // 2) - (text.get_height() // 2)))
        self._window_ref.blit(surf, self._pos)


    def check_clicked(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.on_click()


    def on_click(self):
        if self._function is not None:
            return self._function()



class TitleCard:

    SIZE = Enum('size', [("MEDIUM", 72), ("LARGE", 100)])
    COLOR = (255, 255, 255)

    def __init__(self, window: pygame.Surface, text: str, size: "TitleCard.SIZE", pos: Vector2) -> None:
        self._font = pygame.font.SysFont("Arial", size.value)
        self._text_render = self._font.render(text, True, self.COLOR)
        self._pos = pos
        self._window_ref = window
        self._is_displaying = True

    
    def toggle_display(self) -> None:
        self._is_displaying = not self._is_displaying

    
    def display(self) -> None:
        if self._is_displaying:
            self._window_ref.blit(self._text_render, ((self._pos.x) - (self._text_render.get_width() // 2), 
                                                      (self._pos.y) - (self._text_render.get_height() // 2)))
            


class MainMenu:
    def __init__(self, window: pygame.Surface, parent) -> None:
        self._title_card = TitleCard(window, "Roids!", TitleCard.SIZE.LARGE, Vector2(window.get_rect().center))
        self._window_ref = window
        self._parent = parent
        self._w_width = window.get_width()
        self._w_height = window.get_height()
        self._github_button = Button(window, Vector2(self._w_width - 100,
                                                     self._w_height - 150), 
                                                     100, 150, self._open_github, "See the full project on github!")
        self._play_button = Button(window, Vector2(self._w_width - (self._w_width / 4), 
                                                   self._w_height - (self._w_height / 3)),
                                                   100, 150, self._start_game, "Play")
        self._buttons = [self._github_button, self._play_button]


    def _open_github(self):
        url = "https://github.com/Moonshoes77/Pygame-Asteroids"
        webbrowser.open(url, new=0, autoraise=True)


    def _start_game(self):
        self._parent.state = self._parent.STATE.PLAYING


    def display(self):
        for button in self._buttons:
            button.display()
            button.check_clicked()