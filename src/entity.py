import pygame
from constants import FLOOR_Y
from sprite import Sprite

class Entity:
    def __init__(self, sprite: Sprite = Sprite(), x: int = 0, y: int = 0, velocity_x: int = 0, velocity_y: int = 0):
        self.rect = pygame.Rect((x, y), sprite.size)
        self.sprite = sprite
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.x, self.y = x, y
        self.width, self.height = sprite.size
        self.alive = True
    
    def update_position(self) -> None:
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.update((self.x, self.y), self.rect.size)

    def draw(self, screen: pygame.Surface) -> None:
        self.sprite.draw(screen, self.x, self.y)

    def destroy(self) -> None:
        self.alive = False
    
    def is_colliding(self, rect: pygame.Rect) -> int:
        if isinstance(rect, list):
            return pygame.Rect.collidelist(self.rect, rect)
        else:    
            return pygame.Rect.colliderect(self.rect, rect)
        
    def ground_collision(self) -> bool:
        return self.y + self.rect.height > FLOOR_Y
