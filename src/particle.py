import pygame
import images as im

class Particle:
    # NOTE: Change image/images to sprite/sprites
    def __init__(self, x: int = 0, y: int = 0, image: pygame.Surface|None = None, images: list[pygame.Surface]|None = None, duration: int = 60, scale: float = 1, adjust_pos: bool = True) -> None:
        self.rect = image.get_rect() if image else images[0].get_rect()
        self.width, self.height = self.rect.width * scale, self.rect.height * scale

        if adjust_pos:
            self.x = x - self.width / 2
            self.y = y - self.height / 2
        else:
            self.x, self.y = x, y

        if image:
            if scale != 1:
                self.images = [im.scale_image(image, (self.width, self.height))]
            else:
                self.images = [image]
        else:
            if scale != 1: # Scale all images in particle
                self.images = list(map(lambda i: im.scale_image(i, (self.width, self.height)), images))
            else:
                self.images = images
        self.imagecount = len(self.images)
        self.time_of_spawn = pygame.time.get_ticks()
        self.duration = duration
        self.alive = True
        self.scale = scale

    def draw(self, screen):
        tick = pygame.time.get_ticks()
        if tick - self.duration >= self.time_of_spawn:
            self.alive = False
        else:
            screen.blit(self.images[(tick-self.time_of_spawn)//(self.duration//self.imagecount)-1], (self.x, self.y))
