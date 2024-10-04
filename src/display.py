import pygame
from config import cfg

if cfg.opengl:
    from OpenGL.GL import *

class Display:
    def __init__(self) -> None:
        pygame.init()

        # This is a dictionary of rendered text to avoid rendering text every frame
        # TODO: split text into own class
        self.text_cache = {}

    def draw_image(self, image, dest): pass
    def render_text(self, content: str, color: pygame.Color = 0, antialias: bool = False, opacity: int = 255, x: int = 0, y: int = 0, display: bool = True, id: str = ""): pass
    def display_cached_text(self, id: str = "", x: int = 0, y: int = 0): pass
    def set_cached_text_alpha(self, id: str, opacity: int = 255): pass
    def update(self):
        pygame.display.flip()
        pygame.time.Clock().tick(60)

class PygameDisplay(Display):
    """Display using Pygame Surface"""
    def __init__(self) -> None:
        super().__init__()

        if cfg.display.fullscreen:
            flags = pygame.HWSURFACE | pygame.FULLSCREEN | pygame.SCALED
        else:
            flags = 0

        self.surface = pygame.display.set_mode((cfg.screen_width, cfg.screen_height), flags=flags)
        self.surface.set_alpha(None)
        pygame.display.set_caption("PyPlanes (Pygame)")

        pygame.font.init()
        self.font = pygame.font.Font(size=50)

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

class OpenGLDisplay(Display):
    """Display using OpenGL"""
    def __init__(self) -> None:
        super().__init__()
        if cfg.display.fullscreen:
            flags = pygame.DOUBLEBUF | pygame.OPENGL | pygame.HWSURFACE | pygame.FULLSCREEN | pygame.SCALED
        else:
            flags = pygame.DOUBLEBUF | pygame.OPENGL

        self.surface = pygame.display.set_mode((cfg.screen_width, cfg.screen_height), flags=flags)
        pygame.display.set_caption("PyPlanes (OpenGL)")

        # basic opengl configuration
        glViewport(0, 0, cfg.screen_width, cfg.screen_height)
        glDepthRange(0, 1)
        glMatrixMode(GL_PROJECTION)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glEnable(GL_BLEND)

    def draw_image(self, image, dest):
        # prepare to render the texture-mapped rectangle
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #glClearColor(0, 0, 0, 1.0)

        # draw texture openGL Texture
        glBindTexture(GL_TEXTURE_2D, image)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(-1, 1)
        glTexCoord2f(0, 1); glVertex2f(-1, -1)
        glTexCoord2f(1, 1); glVertex2f(1, -1)
        glTexCoord2f(1, 0); glVertex2f(1, 1)
        glEnd()

# Initialise screen
if cfg.opengl:
    screen = OpenGLDisplay()
else:
    screen = PygameDisplay()
