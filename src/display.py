import pygame
from config import cfg

if cfg.opengl:
    from OpenGL.GL import *
    from OpenGL.GLU import *

class Display:
    def __init__(self) -> None:
        pygame.init()

        # This is a dictionary of rendered text to avoid rendering text every frame
        # TODO: split text into own class
        self.text_cache = {}

    def draw_image(self, image, dest, area = None, **kwargs): pass
    def render_text(self, content: str, color: pygame.Color = 0, antialias: bool = False, opacity: int = 255, display: bool = True, id: str = ""): 
        """Display text onto screen. 
        If id is given, stores in cache.
        If display is False, does not show straight away"""

        if not (display or id): return # no point rendering if not displayed or put in cache

        rendered = self.font.render(content, antialias, color)
        if opacity < 255:
            rendered.set_alpha(opacity)

        if id:
            self.text_cache[id] = rendered

        return rendered

    def display_cached_text(self, id: str = "", x: int = 0, y: int = 0): pass

    def set_cached_text_alpha(self, id: str, opacity: int = 255):
        rendered = self.text_cache.get(id)
        if rendered:
            rendered.set_alpha(opacity)

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

    def draw_image(self, image, dest, area: pygame.Rect = None, **kwargs):
        self.surface.blit(image.image, dest, area)

    def render_text(self, content: str, x: int = 0, y: int = 0, display: bool = True, **kwargs):
        rendered = super().render_text(content, display=display, **kwargs)

        if display:
            self.surface.blit(rendered, (x, y))

    def display_cached_text(self, id: str = "", x: int = 0, y: int = 0):
        """Display text that is stored in the cache"""
        rendered = self.text_cache.get(id)
        if rendered:
            self.surface.blit(rendered, (x, y))

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

        pygame.font.init()
        self.font = pygame.font.Font(size=50)

        glClearColor(*(0,0,0,0))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, cfg.screen_width, cfg.screen_height, 0)

    def display_cached_text(self, id: str = "", x: int = 0, y: int = 0):
        rendered = self.text_cache.get(id)
        if rendered:
            text_data = pygame.image.tostring(rendered, "RGBA", True)
            glWindowPos2d(x, cfg.screen_height-y-+rendered.get_height())
            glDrawPixels(rendered.get_width(), rendered.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
            
        
    def render_text(self, content: str, x: int = 0, y: int = 0, display: bool = True, **kwargs):
        rendered = super().render_text(content, **kwargs)

        if display:
            text_data = pygame.image.tostring(rendered, "RGBA", True)
            glWindowPos2d(x, cfg.screen_height-y-rendered.get_height())
            glDrawPixels(rendered.get_width(), rendered.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    def draw_image(self, image, dest: tuple, area: tuple = None, rotation: int = 0, size: tuple = None, **kwargs):
        # draw texture openGL Texture
        glBindTexture(GL_TEXTURE_2D, image.image) # prepare texture
        glEnable(GL_TEXTURE_2D)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glTranslate(dest[0], dest[1], 0) # set position
        glRotate(-rotation, 0, 0, 1)

        glBegin(GL_QUADS)
        # create quad with texture 
        glVertex(0, 0, 1); glTexCoord2f(0, 0)
        glVertex(image.size[0], 0, 1); glTexCoord2f(0, 1)
        glVertex(image.size[0], image.size[1], 1); glTexCoord2f(1, 1)
        glVertex(0, image.size[1], 1); glTexCoord2f(1, 0)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        #glFlush()

    def update(self):
        super().update()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

# Initialise screen
if cfg.opengl:
    screen = OpenGLDisplay()
else:
    screen = PygameDisplay()
