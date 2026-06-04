import pygame
from pygame import Vector2
from collections.abc import Callable
from enum import Enum

class Button:

    pygame.font.init()
    FONT = pygame.font.SysFont("Arial", 24)

    def __init__(self, window: pygame.Surface,  pos: Vector2, width: int, height: int, function: Callable | None, text: str | None = None):
        self._pos = pos
        self._rect = pygame.Rect(self._pos, (width, height))
        self._text = text
        self._window_ref = window
        self._function = function


    def display(self):
        surf = pygame.Surface(self._rect.size)
        text = self.FONT.render(self._text, True, (255, 255, 255))
        surf.fill((127, 127, 127))
        surf.blit(text, ((surf.get_width() // 2) - (text.get_width() // 2), (surf.get_height() // 2) - (text.get_height() // 2)))
        self._window_ref.blit(surf, self._pos)


    def on_click(self):
        if self._function is not None:
            return self._function()



class TitleCard:

    SIZE = Enum('size', [("MEDIUM", 72), ("LARGE", 90)])
    COLOR = (255, 255, 255)

    def __init__(self, window: pygame.Surface, text: str, size: "TitleCard.SIZE", pos: Vector2) -> None:
        self._font = pygame.font.SysFont("Arial", size.value)
        self._text_render = self._font.render(text, True, self.COLOR)
        self._pos = pos
        self._window_ref = window
        self._is_displaying = False

    
    def toggle_display(self) -> None:
        self._is_displaying = not self._is_displaying

    
    def display(self) -> None:
        if self._is_displaying:
            self._window_ref.blit(self._text_render, ((self._pos.x) - (self._text_render.get_width() // 2), 
                                                      (self._pos.y) - (self._text_render.get_height() // 2)))