import pygame
import math
from config import cfg

class ScreenDistortion:
    """A class that represents special screen effects"""
    def __init__(self, x: int, y: int, velocity: int, direction: int = 0, angle: int = 360, width: int = 10, time_alive: int = 60) -> None:
        self.x, self.y = x, y
        self.velocity = velocity
        self.direction_deg = direction
        self.angle_deg = angle
        self.direction = math.radians(direction)
        self.angle = math.radians(angle)
        self.radius = 0
        self.width = width
        self.alive = True
        self.alpha = 64
        self.time_alive = time_alive - 64 # once this reaches 0, die

    def draw(self, screen: pygame.Surface, scroll_speed: int = cfg.scroll_speed):
        """Display the effect on screen"""
        size = self.radius + 1
        init_direction = self.direction - self.angle // 2

        if cfg.display.advanced_vfx: # Slower but more realistic (distort individual pixels)
            # can we put this on the GPU?
            density = int(size // cfg.display.avfx_step) + 1 # x shifts per degree
            for i in range(self.angle_deg):
                for a in range(-int(density*(cfg.display.avfx_precision//2)), int(density*(cfg.display.avfx_precision//2))):
                    rad = math.radians(i + a/cfg.display.avfx_precision)
                    sr = math.sin(rad)
                    cr = math.cos(rad)

                    for p in range(self.width):
                        pointer_x = int(sr * (size + p) + self.x)
                        pointer_y = int(cr * (size + p) + self.y)

                        if not ( 0 < pointer_x < cfg.screen_width and 0 < pointer_y < cfg.screen_height): # out of bounds
                            continue

                        if cfg.debug.show_distortion:
                            screen.set_at((pointer_x, pointer_y), "0x000000")

                        ref_px = screen.get_at((pointer_x, pointer_y))

                        pointer_x = int(sr * (size + self.width + p) + self.x)
                        pointer_y = int(cr * (size + self.width + p) + self.y)

                        if not ( 0 < pointer_x < cfg.screen_width and 0 < pointer_y < cfg.screen_height):
                            continue

                        if cfg.debug.show_distortion:
                            screen.set_at((pointer_x, pointer_y), "0xFFFFFF")
                        else:
                            screen.set_at((pointer_x, pointer_y), ref_px)

        else: # Faster (change color of pixels using shape)
            arc = pygame.Surface((size, size), pygame.SRCALPHA)

            if cfg.display.fast_vfx:
                # Draw a square outline
                pygame.draw.lines(
                    arc, 
                    "0x888888", 
                    True,
                    [(0, 0), (size, 0), (size, size), (0, size)],
                    self.width)
            else:
                # This is ridiculously slow
                pygame.draw.arc(
                    arc, 
                    "0x888888", 
                    (0, 0, size, size), 
                    init_direction, 
                    self.direction + self.angle // 2,
                    width=self.width)
            
            arc.set_alpha(self.alpha)

            screen.blit(
                arc,
                (self.x - size // 2, self.y - size // 2)
            )

        self.radius += self.velocity
        self.time_alive -= 1

        # gradually fade out
        if -64 < self.time_alive < 0: 
            self.alpha -= 1
        elif self.time_alive <= -64:
            self.alive = False
