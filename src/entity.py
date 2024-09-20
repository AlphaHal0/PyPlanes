import pygame
from constants import SCREEN_HEIGHT
import images

class Entity:
    def __init__(self, rect: pygame.Rect, gravity: int, sprite: pygame.Surface | list | None = None, x: int = 0, y: int = 0, velocity_x: int = 0, velocity_y: int = 0, animation_time: int = 5):
        self.rect = rect
        self.gravity = gravity
        self.sprite = sprite
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.x, self.y = x, y
        self.alive = True
        self.is_animated = isinstance(sprite, list)
        if self.is_animated:
            self.anim_time = animation_time
            self.anim_frame = 0
            self.anim_frame_count = len(sprite)-1
    
    def update_position(self) -> None:
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.update((self.x, self.y), self.rect.size)

    def draw(self, screen: pygame.Surface) -> None:
        if self.sprite is None:
            pygame.draw.rect(screen, (255, 0, 0), self.rect)
        else:
            if self.is_animated:
                frame = self.anim_frame//self.anim_time
                screen.blit(self.sprite[frame], self.rect)
                if frame >= self.anim_frame_count:
                    self.anim_frame = 0
                else:
                    self.anim_frame += 1
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
