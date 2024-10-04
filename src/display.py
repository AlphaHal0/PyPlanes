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

        if cfg.display.fullscreen:
            flags = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.FULLSCREEN | pygame.SCALED
        else:
            flags = pygame.DOUBLEBUF


        self.surface = pygame.display.set_mode((cfg.screen_width, cfg.screen_height), flags=flags)
        self.surface.set_alpha(None)
        self.font = pygame.font.Font(size=50)

        # This is a dictionary of rendered text to avoid rendering text every frame
        # TODO: split text into own class
        self.text_cache = {}

    def draw_image(self, image, dest):
        self.surface.blit(image, dest)

    def render_text(self, content: str, color: pygame.Color = 0, antialias: bool = False, opacity: int = 255, x: int = 0, y: int = 0, display: bool = True, id: str = ""):
        """Display text onto screen. 
        If id is given, stores in cache.
        If display is False, does not show straight away"""

        if not (display or id): return # no point rendering if not displayed or put in cache

        rendered = self.font.render(content, antialias, color)
        if opacity < 255:
            rendered.set_alpha(opacity)

        if id:
            self.text_cache[id] = rendered

        if display:
            self.surface.blit(rendered, (x, y))

    def display_cached_text(self, id: str = "", x: int = 0, y: int = 0):
        """Display text that is stored in the cache"""
        rendered = self.text_cache.get(id)
        if rendered:
            self.surface.blit(rendered, (x, y))

    def set_cached_text_alpha(self, id: str, opacity: int = 255):
        rendered = self.text_cache.get(id)
        if rendered:
            rendered.set_alpha(opacity)

    def update(self):
        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Initialise screen
screen = PygameDisplay()
