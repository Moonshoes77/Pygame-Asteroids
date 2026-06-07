import pygame
from pygame import Vector2
import math
from random import uniform, randint
from enum import Enum

class Asteroid:
    
    STEP_SIZE = 22.9183
    MAX_VEL = 5.5
    SIZE = Enum('size', ['LARGE', 'MEDIUM', 'SMALL'])

    def __init__(self, window: pygame.Surface, pos: Vector2, size: "Asteroid.SIZE") -> None:
        self._window_ref = window
        self._pos = pos
        self._size = size
        self._value = self._set_value() 
        self._r = self._init_radius(self._size)
        self._max_diameter = (self._r * 1.15) * 2
        self._sprite, self.mask = self._make_sprite()
        self._center = Vector2(self._sprite.get_width() // 2, self._sprite.get_height() // 2)
        self._vel = Vector2(uniform(-self.MAX_VEL, self.MAX_VEL), uniform(-self.MAX_VEL, self.MAX_VEL))
        self.rect = self._sprite.get_rect(center=self._pos)
        self.is_alive = True
    
    @property
    def pos(self) -> Vector2:
        return self._pos


    def _set_value(self) -> int:
        if self._size == Asteroid.SIZE.LARGE:
            value = 200
        if self._size == Asteroid.SIZE.MEDIUM:
            value = 400
        if self._size == Asteroid.SIZE.SMALL:
            value = 800
        return value


    def _make_sprite(self) -> tuple:
        variance = self._r * 0.15
        surf = pygame.Surface((self._max_diameter, self._max_diameter), pygame.SRCALPHA)
        mask_surf = pygame.Surface((self._max_diameter, self._max_diameter), pygame.SRCALPHA)
        center = Vector2(surf.get_width() // 2, surf.get_height() // 2)
        angle = 0
        points = []

        while math.radians(angle) < (math.pi * 2):
            points.append(Vector2(center.x - self._r * math.cos(math.radians(angle)) + uniform(-variance, variance), center.y - self._r * -math.sin(math.radians(angle)) + uniform(-variance, variance)))
            angle += self.STEP_SIZE

        pygame.draw.polygon(surf, (255, 255, 255), points, 3)
        pygame.draw.polygon(mask_surf, (255, 255, 255), points)
        mask = pygame.mask.from_surface(mask_surf)

        return (surf, mask)
    
    
    def _init_radius(self, size: "Asteroid.SIZE") -> float:
        match self._size:
            case size.LARGE:
                return uniform(50, 65)
            case size.MEDIUM:
                return uniform(30, 45)
            case size.SMALL:
                return uniform(15, 25)


    def _screen_wrap(self, surface: pygame.Surface, pos: Vector2) -> Vector2:
        x = pos.x
        y = pos.y
        w, h = surface.get_size()
        return Vector2(x % (w + self._max_diameter / 2), y % (h + self._max_diameter / 2))


    def take_damage(self, asteroids_list: list) -> None:

        if self._size == Asteroid.SIZE.SMALL:
            pass
        elif self._size == Asteroid.SIZE.LARGE:
            for i in range(2):
                asteroids_list.append(Asteroid(self._window_ref, self.pos, Asteroid.SIZE.MEDIUM))
        elif self._size == Asteroid.SIZE.MEDIUM:
            for i in range(2):
                asteroids_list.append(Asteroid(self._window_ref, self.pos, Asteroid.SIZE.SMALL))

    
    def award_points(self) -> int:
        return self._value
    

    def update(self) -> None:
        self._pos += self._vel
        self._pos = self._screen_wrap(self._window_ref, self._pos)
        self.rect = self._sprite.get_rect(center=self._pos)


    def display(self) -> None:
        self._window_ref.blit(self._sprite, self.rect)
