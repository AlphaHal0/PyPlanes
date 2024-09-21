import pygame
import images
from config import cfg

class Sprite:
    def __init__(self, image: pygame.Surface|list[pygame.Surface]|None = None, animation_time: int = 1, size: tuple|None = None, size_multiplier: int = 1) -> None:
        self.base_image = image
        self.is_animated = isinstance(image, list)
        self.rotation = 0
        self.size = size
        self.flip_x = False
        self.flip_y = False

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

    def update(self):
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
        if cfg.show_sprite_sizes:
            pygame.draw.rect(screen, (255, 0, 255), ((x,y), self.size))

        if cfg.disable_sprite_textures: return False

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
    
    def flip(self, flip_x: bool = True, flip_y: bool = False, no_update: bool = False):
        self.flip_x, self.flip_y = flip_x, flip_y
        if not no_update: self.update()

    def rotate(self, angle: float, no_update: bool = False):
        self.rotation = angle
        if not no_update: self.update()

    def scale(self, size: tuple, no_update: bool = False):
        self.scale = size,
        if not no_update: self.update()

    def set_size(self, size: tuple, size_multiplier: float = 1, no_update: bool = False):
        self.size = (size[0] * size_multiplier, size[1] * size_multiplier)
        self.scale(self.size, no_update=no_update)
