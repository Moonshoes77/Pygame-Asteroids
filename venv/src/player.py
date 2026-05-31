import pygame
from pygame import Vector2
import math


class Player:

    def __init__(self, window: pygame.Surface) -> None:
        self._pos = Vector2(window.get_width() // 2, window.get_height() // 2)
        self._sprite = self._draw_sprite()
        self._rotated_sprite = self._sprite.copy()
        self._window_ref = window
        self._turn_speed = 2
        self._accel = 2
        self._vel = Vector2(0, 0)
        self._angle = 0
        self._center = Vector2(self._sprite.get_width() // 2, self._sprite.get_height() // 2)
        self._heading = math.radians(self._angle) % (2 * math.pi)
        

    def _get_inputs(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self._rotate(False)
        if keys[pygame.K_RIGHT]:
            self._rotate(True)
        if keys[pygame.K_UP]:
            self._thrust()
        if keys[pygame.K_p]: ### print debug info
            pass

    
    def _draw_sprite(self) -> pygame.Surface:
        img = pygame.Surface((32, 32), pygame.SRCALPHA)
        ship_coords = [(img.get_width() // 2, 0), (img.get_width(), img.get_height()), (img.get_width() // 2, img.get_height() - 5), (0, img.get_height())]
        pygame.draw.polygon(img, (255, 255, 255), ship_coords)
        return img
    

    def _rotate(self, clockwise: bool) -> None:
        direction = -1 if clockwise else 1
        self._angle += self._turn_speed * direction
        self._heading = math.radians(self._angle) % (2 * math.pi)

    
    def _thrust(self):
        self._vel.x += self._accel * math.cos(self._heading)
        self._vel.y += self._accel * -math.sin(self._heading)
        self._vel.clamp_magnitude_ip(0.0, 5.0)

    
    def _screen_wrap(self, surface: pygame.Surface, pos: Vector2):
        x = pos.x
        y = pos.y
        w,h = surface.get_size()
        return Vector2(x % (w + 10), y % (h + 10))


    def update(self):
        self._get_inputs()
        self._pos += self._vel
        self._pos = self._screen_wrap(self._window_ref, self._pos)
        print(f"heading: {self._heading}")


    def display(self) -> None:
        rotated_sprite = pygame.transform.rotate(self._sprite, math.degrees(self._heading - (math.pi / 2)))
        offset_x = rotated_sprite.get_width() // 2
        offset_y = rotated_sprite.get_height() // 2
        self._window_ref.blit(rotated_sprite, (self._pos.x - offset_x, self._pos.y - offset_y))
        line_len = 50
        endpoint_x = self._pos.x + math.cos(self._heading) * line_len
        endpoint_y = self._pos.y + -math.sin(self._heading) * line_len
        pygame.draw.line(self._window_ref, (255, 0, 0), (self._pos.x, self._pos.y), (endpoint_x, endpoint_y), 1)
