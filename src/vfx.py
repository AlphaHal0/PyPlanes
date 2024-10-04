import pygame
import math
from config import cfg
from display import screen

try:
    #import cupy
    import numpy
    cupy_installed = True
except ImportError:
    cupy_installed = False
    print("[!!!] Cupy and Numpy are not installed. Advanced VFX will not be available")

class ScreenDistortion:
    """A class that represents special screen effects"""
    def __init__(self, x: int, y: int, velocity: int, direction: int = 0, angle: int = 360, width: int = 10, time_alive: int = 60, move_with_screen: bool = False) -> None:
        self.x, self.y = x, y
        self.velocity = velocity
        self.direction = direction
        self.angle = angle
        self.radius = 0
        self.width = width
        self.alive = True
        self.alpha = 64
        self.move_with_screen = move_with_screen
        self.time_alive = time_alive - 64 # once this reaches 0, die

    def draw(self, scroll_speed: int = cfg.scroll_speed):
        """Display the effect on screen"""
        size = self.radius + 1
        init_direction = self.direction - self.angle // 2

        if cfg.display.advanced_vfx and cupy_installed: # Slower but more realistic (distort individual pixels)
            screen.surface.lock() # lock to be processed
            c = numpy.frombuffer(screen.surface.get_view('1'), numpy.uint8)\
                .reshape(cfg.screen_height, cfg.screen_width, 4) # Convert screen buffer to array
            density = size / cfg.display.avfx_step + 1 # x shifts per degree
            for i in range(init_direction, init_direction + self.angle):
                for a in range(-int(density*(cfg.display.avfx_precision//2)), int(density*(cfg.display.avfx_precision//2))):
                    rad = numpy.radians(i + a/cfg.display.avfx_precision + 90)
                    sr = numpy.sin(rad)
                    cr = numpy.cos(rad)
                    numpy.cuda.Stream.null.synchronize()

                    for p in range(self.width):
                        pointer_x = int(sr * (size + p) + self.x)
                        pointer_y = int(cr * (size + p) + self.y)

                        if not ( 0 < pointer_x < cfg.screen_width and 0 < pointer_y < cfg.screen_height): # out of bounds
                            continue

                        if cfg.debug.show_distortion:
                            c[pointer_y][pointer_x] = [0, 0, 0, 255]

                        ref_px = c[pointer_y][pointer_x]

                        pointer_x = int(sr * (size + self.width + p) + self.x)
                        pointer_y = int(cr * (size + self.width + p) + self.y)

                        if not ( 0 < pointer_x < cfg.screen_width and 0 < pointer_y < cfg.screen_height):
                            continue

                        if cfg.debug.show_distortion:
                            c[pointer_y][pointer_x] = [255, 255, 255, 255]
                        else:
                            c[pointer_y][pointer_x] = ref_px
            screen.surface.unlock()

        else: # Faster (change color of pixels using shape)
            arc = pygame.Surface((size+self.width, size+self.width), pygame.SRCALPHA)

            if cfg.display.fast_vfx:
                # Draw a square outline
                pygame.draw.lines(
                    arc, 
                    "0x888888", 
                    True,
                    [(0, 0), (size, 0), (size, size), (0, size)],
                    self.width)
            else:
                pygame.draw.arc(
                    arc, 
                    "0x888888", 
                    (0, 0, size, size), 
                    math.radians(init_direction), 
                    math.radians(init_direction + self.angle),
                    width=self.width)
            
            arc.set_alpha(self.alpha)

            screen.surface.blit(
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

        if self.move_with_screen: self.x -= scroll_speed
