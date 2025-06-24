# type checking without circular import
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game

import pygame
from config import cfg
from sprite import Sprite
import math

class Entity:
    """Base class for all entities in the game.
    By default, Entities move by their velocity each tick. """
    def __init__(self, game: Game, sprite: Sprite|None = None, x: int = 0, y: int = 0, velocity_x: int = 0, velocity_y: int = 0, rotation: int = 0, adj_velocity_for_rot: bool = True, spawn_cooldown: int = cfg.gameplay.spawn_cooldown, collision_mask: list|int = []):
        if sprite is None: sprite = Sprite()

        self.game = game
        self.sprite = sprite
        self.x, self.y = x, y
        self.width, self.height = sprite.size
        self.rect = pygame.Rect((x, y), sprite.size)
        self.rotation = rotation

        if isinstance(collision_mask, int):
            self.collision_mask = [collision_mask] # convert to list if not already
        else:
            self.collision_mask = collision_mask

        self.spawn_cooldown = spawn_cooldown
        self.time_of_spawn = pygame.time.get_ticks()
        self.alive = True

        if rotation: self.sprite.rotate(rotation)

        if adj_velocity_for_rot and rotation:
            # Rotate velocity vector to match sprite rotation
            # Used for bullets and bombs, etc.
            rad = math.radians(-rotation)
            sr = math.sin(rad)
            cr = math.cos(rad)
            self.velocity_x = velocity_x * cr - velocity_y * sr
            self.velocity_y = velocity_x * sr + velocity_y * cr
        else:
            self.velocity_x = velocity_x
            self.velocity_y = velocity_y

        self.game.entities.append(self)
        self.index = len(self.game.entities) - 1

    def apply_rotated_velocity(self, force: float, direction: int|None = None):
        """Apply a force to this Entity with a direction"""
        if direction == None:
            direction = self.rotation
            rad = math.radians(-direction)
            self.velocity_x += force * math.cos(rad)
            self.velocity_y += force * math.sin(rad)

    def update(self) -> None:
        """Update the position of the Entity using its velocity"""
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.update((self.x, self.y), self.rect.size)
        self.draw()

    def draw(self) -> None:
        """Draws the Entity onto the screen"""
        self.sprite.draw(self.x, self.y)

    def destroy(self) -> None:
        self.alive = False

    def is_colliding(self, mask: list|int = [], ignore_self: bool = True) -> list:
        """Returns if this Entity is colliding with other Entities with this collision mask"""
        if isinstance(mask, int): mask = [mask] # convert to list if not already
        colliding = []

        for entity in self.game.entities:
            if ignore_self and entity == self: continue

            for i in mask:
                if i in entity.collision_mask and pygame.Rect.colliderect(self.rect, entity.rect):
                    colliding.append(entity)
                    break

        return colliding

    def distance_to(self, x: int, y: int) -> float:
        """Returns the distance from this Entity to (x, y)"""
        dx = min(abs(x - self.x), abs(x - (self.x + self.width)))**2
        dy = min(abs(y - self.y), abs(y - (self.y + self.height)))**2

        return math.sqrt(dx+dy)

    def ground_collision(self) -> bool:
        """Returns if this Entity is colliding with the ground"""
        return self.y + self.height >= cfg.floor_y

    def hit(self) -> bool:
        """Function run when hit
        Entity does not implement this, it should be implemented for child classes e.g. Aircraft"""
        return False
