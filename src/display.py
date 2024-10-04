import pygame
from config import cfg

class Display:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()

class PygameDisplay(Display):
    """Display using Pygame Surface"""
    def __init__(self) -> None:
        super().__init__()
        self.surface = pygame.display.set_mode((cfg.screen_width, cfg.screen_height), flags=pygame.DOUBLEBUF)
        self.surface.set_alpha(None)
        self.font = pygame.font.Font(size=50)

    def draw_image(self, image, dest):
        self.surface.blit(image, dest)

    def update(self):
        pygame.display.update()
        pygame.time.Clock().tick(60)

# Initialise screen
screen = PygameDisplay()
