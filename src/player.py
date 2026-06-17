import pygame
from pygame import Vector2
import math
from enum import Enum

class Player:

    DECEL_RATE = 0.982
    MAX_VELOCITY = 5.6
    STATE = Enum("state", ["VULNERABLE", "INVULNERABLE"])

    def __init__(self, window: pygame.Surface, projectile_list: list) -> None:
        self.COLOR = tuple([255, 255, 255])
        self._pos = Vector2(window.get_width() // 2, window.get_height() // 2)
        self._sprite = self._draw_sprite()
        self._rotated_sprite = self._sprite.copy()
        self._rect = self._rotated_sprite.get_rect(center=self._pos)
        self._window_ref = window
        self._turn_speed = 2
        self._accel = 0.25
        self._vel = Vector2(0, 0)
        self._angle = 90
        self._counter = 0
        self._heading = math.radians(self._angle) % (2 * math.pi)
        self._mask = pygame.mask.from_surface(self._rotated_sprite)
        self._projectile_list = projectile_list
        self._state = self.STATE.VULNERABLE

        

    
    def __str__(self):
        return f"Player obj., pos: {self._pos}, heading: {self._heading}"
    

    @property
    def state(self) -> STATE:
        return self._state

    @property
    def pos(self) -> Vector2:
        return self._pos

    @property
    def vel(self) -> Vector2:
        return self._vel

    @property
    def heading(self) -> float:
        return self._heading

    @property
    def rect(self):
        return self._rect

    @property
    def sprite(self) -> pygame.Surface:
        return self._sprite

    @property
    def mask(self) -> pygame.Mask:
        return self._mask


    def _get_inputs(self, events_list: list) -> None:
        keys = pygame.key.get_pressed()        
        if keys[pygame.K_LEFT]:
            self._rotate(False)
        if keys[pygame.K_RIGHT]:
            self._rotate(True)
        if keys[pygame.K_UP]:
            self._thrust()
        for event in events_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._shoot()

    
    def _draw_sprite(self) -> pygame.Surface:
        img = pygame.Surface((32, 32), pygame.SRCALPHA)
        ship_coords = [(img.get_width() // 2, 0), (img.get_width(), img.get_height()), (img.get_width() // 2, img.get_height() - 5), (0, img.get_height())]
        pygame.draw.polygon(img, (255, 255, 255), ship_coords)
        self._mask = pygame.mask.from_surface(img)
        return img
    

    def _rotate(self, clockwise: bool) -> None:
        direction = -1 if clockwise else 1
        self._angle += self._turn_speed * direction
        self._heading = math.radians(self._angle) % (2 * math.pi)

    
    def _thrust(self) -> None:
        self._vel.x += self._accel * math.cos(self._heading)
        self._vel.y += self._accel * -math.sin(self._heading)
        self._vel.clamp_magnitude_ip(0.0, self.MAX_VELOCITY)


    def _shoot(self):
        self._projectile_list.append(Bullet(self, self._window_ref))
    
    def _screen_wrap(self, surface: pygame.Surface, pos: Vector2) -> Vector2:
        x, y = pos
        w, h = surface.get_size()
        return Vector2(x % (w + 20), y % (h + 20))
    

    def collide(self, asteroid) -> tuple | None:
        offset = (asteroid.rect.x - self._rect.x, asteroid.rect.y - self._rect.y)
        return self._mask.overlap(asteroid.mask, offset)        


    def set_invulnerable(self) -> None:
        self._state = self.STATE.INVULNERABLE

    
    def set_vulnerable(self) -> None:
        self._state = self.STATE.VULNERABLE


    def update(self, event_list: list) -> None:
        self._get_inputs(event_list)
        self._pos += self._vel
        self._vel *= self.DECEL_RATE
        self._pos = self._screen_wrap(self._window_ref, self._pos)
        self._rotated_sprite = pygame.transform.rotate(self._sprite, math.degrees(self._heading - (math.pi / 2)))
        self._rect = self._rotated_sprite.get_rect(center=self._pos)
        self._mask = pygame.mask.from_surface(self._rotated_sprite)
        self._counter += 1
        if self._counter > 1000:
            self._counter = 0

    def display(self) -> None:
        if self._state == self.STATE.VULNERABLE:
            self._window_ref.blit(self._rotated_sprite, self._rect)
        elif self._state == self.STATE.INVULNERABLE:
            if self._counter & 20 > 10:
                self._window_ref.blit(self._rotated_sprite, self.rect)

                

class Bullet:

    BULLET_SPEED = 7
    LIFESPAN = 85

    def __init__(self, parent: Player, window: pygame.Surface) -> None:
        self._vel = Vector2(self.BULLET_SPEED * math.cos(parent.heading), self.BULLET_SPEED * (-math.sin(parent.heading))) + parent.vel
        self._pos = parent.pos.copy()
        self._sprite = self._draw_sprite()
        self._rect = self._sprite.get_rect(center=self._pos)
        self._window_ref = window
        self._mask: pygame.Mask = self._make_mask(self._sprite)
        self._counter = 0
        self.is_alive = True


    def _draw_sprite(self) -> pygame.Surface:
        sprite = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(sprite, (255, 255, 255), sprite.get_rect().center, 2)
        # sprite = pygame.transform.scale(sprite, (3, 1))
        return sprite
    
    def _make_mask(self, sprite: pygame.Surface):
        ### make the whole surface a filled mask to reduce bullets traveling through asteroids ###
        mask = pygame.Mask(sprite.get_size())
        mask.fill()
        return mask
    

    def _screen_wrap(self, surface: pygame.Surface, pos: Vector2) -> Vector2:
        x, y = pos
        w, h = surface.get_size()
        return Vector2(x % (w + 20), y % (h + 20))
    

    def collide(self, asteroid) -> tuple | None:
        offset = (asteroid.rect.x - self._rect.x, asteroid.rect.y - self._rect.y)
        return self._mask.overlap(asteroid.mask, offset) 

    def update(self) -> None:
        if self.is_alive:
            self._pos += self._vel
            self._pos = self._screen_wrap(self._window_ref, self._pos)
            self._rect = self._sprite.get_rect(center=self._pos)
            self._counter += 1
        if self._counter == self.LIFESPAN:
            self.is_alive = False


    def display(self, window: pygame.Surface) -> None:
        window.blit(self._sprite, (self._pos.x - (self._sprite.get_width() / 2), self._pos.y - (self._sprite.get_height() / 2)))
        
