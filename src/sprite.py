import pygame
import images
from constants import DISABLE_SPRITE_TEXTURES, SHOW_SPRITE_SIZES

class Sprite:
    def __init__(self, image: pygame.Surface|list[pygame.Surface]|None = None, animation_time: int = 1, size: tuple|None = None, size_multiplier: int = 1) -> None:
        self.image = image
        self.is_animated = isinstance(image, list)

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

        if image: self.set_size(size, size_multiplier)

    def draw(self, screen: pygame.Surface, x: int, y: int, loop: bool = True) -> bool:
        if SHOW_SPRITE_SIZES:
            pygame.draw.rect(screen, (255, 0, 255), ((x,y), self.size))
            
        if DISABLE_SPRITE_TEXTURES: return False

        if self.image is None:
            pygame.draw.rect(screen, (255, 0, 255), ((x,y), self.size))
        else:
            if self.is_animated:
                frame = self.anim_frame//self.anim_time
                if frame >= self.anim_frame_count:
                    if loop: self.anim_frame = 0
                    else: return False
                else:
                    self.anim_frame += 1
                    screen.blit(self.image[frame], ((x,y), self.size))
            else:
                    screen.blit(self.image, ((x,y), self.size))

        return True
    
    def flip(self, flip_x: bool = True, flip_y: bool = False):
        if self.is_animated:
            image = list(map(lambda x: images.flip_image(x, flip_x, flip_y), self.image))
            self.image = image
        else:
            self.image = images.flip_image(self.image, flip_x, flip_y)

    def rotate(self, angle: float):
        if self.is_animated:
            image = list(map(lambda x: pygame.transform.rotate(x, angle), self.image))
            self.image = image
        else:
            self.image = pygame.transform.rotate(self.image, angle)

    def scale(self, size: tuple):
        if self.is_animated:
            image = list(map(lambda x: pygame.transform.scale(x, size), self.image))
            self.image = image
        else:
            self.image = pygame.transform.scale(self.image, size)

    def set_size(self, size: tuple, size_multiplier: float = 1):
        self.size = (size[0] * size_multiplier, size[1] * size_multiplier)
        self.scale(self.size)
