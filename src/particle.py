import pygame
import images as im
from sprite import Sprite

class Particle:
    def __init__(self, x: int = 0, y: int = 0, sprite: Sprite = Sprite(), duration: int = 60, scale: float = 1, adjust_pos: bool = True) -> None:
        self.sprite = sprite
        self.width, self.height = sprite.size

        if adjust_pos:
            self.x = x - self.width / 2
            self.y = y - self.height / 2
        else:
            self.x, self.y = x, y
        
        self.duration = duration
        self.sprite.anim_time = duration // self.sprite.anim_frame_count
        self.alive = True

    def draw(self, screen):
        self.alive = self.sprite.draw(screen, self.x, self.y, False)
