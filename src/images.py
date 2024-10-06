import config
from config import cfg
import pygame
from texture import Texture
if cfg.opengl:
    from OpenGL.GL import *

try:
    import PIL.Image
    PIL_IMPORTED = True
except ImportError:
    PIL_IMPORTED = False

def load_image(file: str, alpha: bool = True) -> pygame.Surface:
    """Loads an image from file and returns a pygame.Surface.
    Checks `./mod/res/img/{file}` first, then `./res/img/{file}`.
    """
    try:
        img = pygame.image.load(f"./mod/res/img/{file}")
    except FileNotFoundError:
        img = pygame.image.load(f"./res/img/{file}")

    # Only convert with alpha if needed
    if alpha:
        return img.convert_alpha()
    else:
        return img.convert()

def scale_image(surface: pygame.Surface, size: list|float, relative: bool = True) -> pygame.Surface:
    """Returns a scaled pygame.Surface by size.
    If relative is True, the surface is scaled as a fraction of the screen size.
    e.g. 0.1 returns a Surface that is 0.1 times the screen height
    and [0.1, 0.2] returns a Surface that is 0.1x height and 0.2x width."""
    if relative:
        if isinstance(size, list):
            return pygame.transform.scale(surface, (size[0] * cfg.screen_width, size[1] * cfg.screen_height))
        else:
            size *= cfg.screen_height
            return pygame.transform.scale(surface, (size*(surface.get_width()/surface.get_height()), size))
    else:
        return pygame.transform.scale(surface, size)

def flip_image(surface: pygame.Surface, flip_x: bool = True, flip_y: bool = False) -> pygame.Surface:
    """Flips a pygame.Surface"""
    return pygame.transform.flip(surface, flip_x, flip_y)

def surface_to_texture(surface: pygame.Surface):
    """Converts a surface to an OpenGL texture, if OpenGL is enabled"""
    if not cfg.opengl: return Texture(surface, surface.get_size())

    w, h = surface.get_size()
    img_data = pygame.image.tostring(surface, 'RGBA')

    texID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glEnable(GL_TEXTURE_2D)

    return Texture(texID, (w, h))

class ImageCategory:
    """A class that handles an image category.
    ImageHandler initialises this class and manually sets attributes for it."""
    def __init__(self) -> None:
        pass

class ImageHandler:
    """Class to manage images.
    Images are loaded from a Config and stored as attributes"""
    def __init__(self, con: config.Config) -> None:
        self.con = con
        self.load()

    def load(self):
        for cat, contents in self.con.d.items(): # search categories
            setattr(self, cat, ImageCategory())
            for key, value in contents.items(): # search category items
                if value.get('anim'): # this is an animated image
                    images = []
                    if value.get('mode').startswith('s'):
                        for i in range(value['anim']):
                            # e.g. if value['fp'] was "frame_{}.png" then it loads ["frame_1.png", "frame_2.png", ...]
                            images.append(self.process_image(value, value['fp'].format(i)))
                    elif PIL_IMPORTED:
                        # Load and split image
                        if cfg.debug.show_image_inits: print("load img", value['fp'] + ".png", end=' ')
                        try:
                            image = PIL.Image.open(f"./mod/res/img/{value['fp']}.png")
                            if cfg.debug.show_image_inits: print("...ok")
                        except FileNotFoundError: 
                            try: 
                                image = PIL.Image.open(f"./res/img/{value['fp']}.png")
                                if cfg.debug.show_image_inits: print("...ok")
                            except FileNotFoundError:
                                if cfg.debug.show_image_inits: print("...NOT FOUND")
                                setattr(getattr(self, cat), key, None)
                                continue
                        
                        for i in range(value['anim']):
                            if value['mode'].startswith('x'): # split horizontally
                                new_image = image.crop(((i)*(image.width//value['anim']), 0, (i+1)*(image.width//value['anim']), image.height))
                            else: # split vertically
                                new_image = image.crop((0, (i)*(image.height//value['anim']), image.width, (i+1)*(image.height//value['anim'])))

                            images.append(self.process_image(value, image=
                                pygame.image.fromstring(new_image.tobytes(), new_image.size, new_image.mode).convert_alpha())) # Convert PIL Image to Pygame image
                    else:
                        print(f"[!!!] Image {key} could not be loaded because Pillow has not been installed. Please install it and try again")
                        setattr(getattr(self, cat), key, None)
                        continue
                    setattr(getattr(self, cat), key, images)
                else:
                    setattr(getattr(self, cat), key, self.process_image(value))

    def process_image(self, value: dict, fp_override: str = "", image: pygame.Surface|None = None) -> pygame.Surface|None:
        """Loads and processes an image based on the contents in value.
        Available functions:
        - fp (str, required): the path to the image (.png ext. added automatically)
        - flip (dict, optional): settings to flip image
        -   flip.x // flip.y (bools, optional): axes to flip on
        - scale (list|float, optional): settings to scale image
        -   if scale is a float, keeps proportions and scales as a fraction of screen height
        -   if scale is a list, scales based on screen width and height
        - relative (bool, optional): if true, scales by pixel values instead of fractions (not recommended)

        If `fp_override` is given, loads that file instead.
        Returns None if not found (Sprites should handle being given None automatically)"""

        if image is None:
            if cfg.debug.show_image_inits: print("load img", fp_override if fp_override else value['fp'], end=' ')
            try:
                image = load_image((fp_override if fp_override else value['fp']) + '.png', value.get('alpha', True))
                if cfg.debug.show_image_inits: print("...ok")
            except FileNotFoundError:
                if cfg.debug.show_image_inits: print("...NOT FOUND")
                return None
        

        if value.get('flip'): 
            image = flip_image(image, value['flip'].get('x', False), value['flip'].get('y', False))

        if value.get('scale'):
            image = scale_image(image, value['scale'], value.get('relative', True))

        return surface_to_texture(image)

image_toc = config.Config("cfg/images.json")
image_toc.reset()
im = ImageHandler(image_toc)
