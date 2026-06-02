import pygame
from pygame import Vector2
import math



class Player:

    DECEL_RATE = 0.982
    MAX_VELOCITY = 5.5

    def __init__(self, window: pygame.Surface) -> None:
        self.COLOR = tuple([255, 255, 255])
        self._pos = Vector2(window.get_width() // 2, window.get_height() // 2)
        self._sprite = self._draw_sprite()
        self._rotated_sprite = self._sprite.copy()
        self._rect = self._rotated_sprite.get_rect(center=self._pos)
        self._window_ref = window
        self._turn_speed = 2
        self._accel = 0.25
        self._vel = Vector2(0, 0)
        self._angle = 0
        self._heading = math.radians(self._angle) % (2 * math.pi)
        self.mask = pygame.mask.from_surface(self._rotated_sprite)
    

    def __str__(self):
        return f"Player obj. pos: {self._pos}, heading: {self._heading}"
    

    @property
    def pos(self) -> Vector2:
        return self._pos
        

    def _get_inputs(self) -> None:
        keys = pygame.key.get_pressed()        
        if keys[pygame.K_LEFT]:
            self._rotate(False)
        if keys[pygame.K_RIGHT]:
            self._rotate(True)
        if keys[pygame.K_UP]:
            self._thrust()

    
    def _draw_sprite(self) -> pygame.Surface:
        img = pygame.Surface((32, 32), pygame.SRCALPHA)
        ship_coords = [(img.get_width() // 2, 0), (img.get_width(), img.get_height()), (img.get_width() // 2, img.get_height() - 5), (0, img.get_height())]
        pygame.draw.polygon(img, (255, 255, 255), ship_coords)
        self.mask = pygame.mask.from_surface(img)
        return img
    

    def _rotate(self, clockwise: bool) -> None:
        direction = -1 if clockwise else 1
        self._angle += self._turn_speed * direction
        self._heading = math.radians(self._angle) % (2 * math.pi)

    
    def _thrust(self) -> None:
        self._vel.x += self._accel * math.cos(self._heading)
        self._vel.y += self._accel * -math.sin(self._heading)
        self._vel.clamp_magnitude_ip(0.0, self.MAX_VELOCITY)

    
    def _screen_wrap(self, surface: pygame.Surface, pos: Vector2) -> Vector2:
        x, y = pos
        w, h = surface.get_size()
        return Vector2(x % (w + 20), y % (h + 20))
    

    def collide(self, asteroid) -> tuple | None:
        offset = (asteroid.rect.x - self._rect.x, asteroid.rect.y - self._rect.y)
        return self.mask.overlap(asteroid.mask, offset)        


    def update(self) -> None:
        self._get_inputs()
        self._pos += self._vel
        self._vel *= self.DECEL_RATE
        self._pos = self._screen_wrap(self._window_ref, self._pos)
        self._rotated_sprite = pygame.transform.rotate(self._sprite, math.degrees(self._heading - (math.pi / 2)))
        self._rect = self._rotated_sprite.get_rect(center=self._pos)
        self.mask = pygame.mask.from_surface(self._rotated_sprite)



    def display(self) -> None:
        self._window_ref.blit(self._rotated_sprite, self._rect)

    
