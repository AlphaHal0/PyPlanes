import pygame
from constants import SCREEN_HEIGHT
import images

class Entity:
    def __init__(self, rect: pygame.Rect, gravity: int, sprite=None):
        self.rect = rect
        self.gravity = gravity
        self.sprite = sprite
        self.velocity = (0, 0)
        self.alive = True
    
    def update_position(self):
        self.rect.move_ip(*self.velocity)

    def draw(self, screen):
        if self.sprite is None:
            pygame.draw.rect(screen, (255, 0, 0), self.rect)
        else:
            screen.blit(self.sprite, self.rect)

    def destroy(self):
        self.alive = False
    
    def is_colliding(self, rect: pygame.Rect):
        if isinstance(rect, list):
            return pygame.Rect.collidelist(self.rect, rect)
        else:    
            return pygame.Rect.colliderect(self.rect, rect)
        
    def ground_collision(self):
        return self.y + self.rect.height > SCREEN_HEIGHT - (0.12 * SCREEN_HEIGHT)

class Moth(Entity):
    def __init__(self, rect, x, y, is_enemy = False):
        super().__init__(rect, 0, images.moth_images)
