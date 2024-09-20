import pygame
from constants import SCREEN_HEIGHT
import images

class Entity:
    def __init__(self, rect: pygame.Rect, gravity: int, sprite: pygame.Surface | None = None, x: int = 0, y: int = 0, velocity_x: int = 0, velocity_y: int = 0):
        self.rect = rect
        self.gravity = gravity
        self.sprite = sprite
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.x = x
        self.y = y
        self.alive = True
    
    def update_position(self) -> None:
        self.rect.move_ip(self.velocity_x, self.velocity_y)
        self.x += self.velocity_x
        self.y += self.velocity_y

    def draw(self, screen: pygame.Surface) -> None:
        if self.sprite is None:
            pygame.draw.rect(screen, (255, 0, 0), self.rect)
        else:
            screen.blit(self.sprite, self.rect)

    def destroy(self) -> None:
        self.alive = False
    
    def is_colliding(self, rect: pygame.Rect) -> int:
        if isinstance(rect, list):
            return pygame.Rect.collidelist(self.rect, rect)
        else:    
            return pygame.Rect.colliderect(self.rect, rect)
        
    def ground_collision(self) -> bool:
        return self.y + self.rect.height > SCREEN_HEIGHT - (0.12 * SCREEN_HEIGHT)

class Moth(Entity):
    def __init__(self, rect, x, y, is_enemy = False):
        super().__init__(rect, 0, images.moth_images)
