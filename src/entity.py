import pygame
from config import cfg
from sprite import Sprite
import math

class Entity:
    """Base class for all entities in the game. 
    By default, Entities move by their velocity each tick. """
    def __init__(self, sprite: Sprite = Sprite(), x: int = 0, y: int = 0, velocity_x: int = 0, velocity_y: int = 0, rotation: int = 0, adj_velocity_for_rot: bool = True):
        self.rect = pygame.Rect((x, y), sprite.size)
        self.x, self.y = x, y
        self.width, self.height = sprite.size
        self.sprite = sprite # UwU

        self.alive = True
        
        if rotation: self.sprite.rotate(rotation)

        if adj_velocity_for_rot and rotation:
            rad = math.radians(-rotation)
            sr = math.sin(rad)
            cr = math.cos(rad)
            self.velocity_x = velocity_x * cr - velocity_y * sr
            self.velocity_y = velocity_x * sr + velocity_y * cr
        else:
            self.velocity_x = velocity_x
            self.velocity_y = velocity_y
    
    def update(self) -> None:
        """Update the position of the Entity using its velocity"""
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.update((self.x, self.y), self.rect.size)

    def draw(self, screen: pygame.Surface) -> None:
        """Draws the Entity onto a pygame.Surface"""
        self.sprite.draw(screen, self.x, self.y)

    def destroy(self) -> None:
        self.alive = False
    
    def is_colliding(self, rect: pygame.Rect) -> int:
        """Returns if this Entity is colliding with a Rect or a list of Rects"""
        if isinstance(rect, list):
            return pygame.Rect.collidelist(self.rect, rect)
        else:    
            return pygame.Rect.colliderect(self.rect, rect)
        
    def distance_to(self, x: int, y: int) -> float:
        """Returns the distance from this Entity to (x, y)"""
        dx = min(abs(x - self.x), abs(x - (self.x + self.width)))**2
        dy = min(abs(y - self.y), abs(y - (self.y + self.height)))**2

        return math.sqrt(dx+dy)
        
    def ground_collision(self) -> bool:
        """Returns if this Entity """
        return self.y + self.height >= cfg.floor_y
