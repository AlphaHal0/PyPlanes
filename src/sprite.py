import pygame
from config import cfg
import math

class Sprite:
    """A class to manage an image or animated list of images with transformation."""
    def __init__(self, image: pygame.Surface|list[pygame.Surface]|None = None, 
    animation_time: int = 1, size: tuple|None = None, size_multiplier: int = 1, 
    rotation: int = 0, flip_x: bool = False, flip_y: bool = False) -> None:
        
        self.base_image = image
        self.is_animated = isinstance(image, list)
        self.rotation = rotation
        self.flip_x = flip_x
        self.flip_y = flip_y

        if self.is_animated:
            if not size: size = image[0].get_size()
            self.anim_time = animation_time
            self.anim_frame = 0
            self.anim_frame_count = len(image)-1
        else:
            if image:
                if not size: size = image.get_size()
            else:
                size = (100, 100)

        self.base_size = size
        if image: self.set_size(size, size_multiplier)

    def update(self):
        """Reloads this sprite with its transformation values.
        If animated, this does so with each of its frames."""
        if self.is_animated:
            image = []
            for i in self.base_image:
                image.append(pygame.transform.rotate(
                    pygame.transform.flip(
                        pygame.transform.scale(
                            i,
                            self.size
                        ),
                        self.flip_x, self.flip_y
                    ),
                    self.rotation
                ))
            self.image = image
        else:
            self.image = pygame.transform.rotate(
                pygame.transform.flip(
                    pygame.transform.scale(
                        self.base_image,
                        self.size
                    ),
                    self.flip_x, self.flip_y
                ),
                self.rotation
            )

    def draw(self, screen: pygame.Surface, x: int, y: int, loop: bool = True) -> bool:
        """Renders this Sprite onto a pygame.Surface, with debug drawing if enabled.
        If textures are disabled, returns False.
        If loop is False and this sprite has run through all of its animation frames, returns False.
        Otherwise, returns True"""
        if cfg.debug.show_sprite_sizes:
            pygame.draw.rect(screen, (255, 0, 255), ((x,y), self.size))
            rad = math.radians(self.rotation)
            pygame.draw.line(screen, (0, 0, 255), (x, y), (math.sin(rad) * 50 + x, math.cos(rad) * 50 + y), 5) # Points upwards (at 0 degrees) 
            pygame.draw.line(screen, (0, 255, 0), (x, y), (math.cos(rad) * 100 + x, -(math.sin(rad) * 100) + y), 5) # Points forward (at 90 degrees)

        if cfg.debug.disable_sprite_textures: return False

        if self.image is None:
            pygame.draw.rect(screen, (255, 0, 255), ((x,y), self.size))
        else:
            if self.is_animated:
                frame = self.anim_frame//self.anim_time
                if frame >= self.anim_frame_count:
                    self.anim_frame = 0
                    if not loop: return False
                else:
                    self.anim_frame += 1
                    screen.blit(self.image[frame], ((x,y), self.size))
            else:
                    screen.blit(self.image, ((x,y), self.size))

        return True
    
    def flip(self, flip_x: bool = True, flip_y: bool = False, no_update: bool = False):
        """Flips the texture of this Sprite.
        If no_update is True, does not apply to this Sprite's images immediately"""
        self.flip_x, self.flip_y = flip_x, flip_y
        if not no_update: self.update()

    def rotate(self, angle: float, no_update: bool = False):
        """Rotates the texture of this Sprite.
        If no_update is True, does not apply to this Sprite's images immediately"""
        self.rotation = angle
        if not no_update: self.update()

    def set_size(self, size: tuple|None = None, size_multiplier: float = 1, no_update: bool = False):
        """Sets the size of this Sprite.
        If size is not given, use the size of this sprite's (first) image.
        The result is scaled by size_multiplier.
        If no_update is True, does not apply to this Sprite's images immediately"""
        if size is None:
            self.size = (self.base_size[0] * size_multiplier, self.base_size[1] * size_multiplier)
        else:
            self.base_size = size    
            self.size = (size[0] * size_multiplier, size[1] * size_multiplier)
        if not no_update: self.update()
