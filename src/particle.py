import pygame

class Particle:
    def __init__(self, x, y, image=None, images=None, duration=60) -> None:
        self.x = x
        self.y = y
        if image:
            self.images = [image]
        else:
            self.images = images
        self.imagecount = len(self.images)
        self.time_of_spawn = pygame.time.get_ticks()
        self.duration = duration
        self.alive = True

    def draw(self, screen):
        tick = pygame.time.get_ticks()
        if tick - self.duration >= self.time_of_spawn:
            self.alive = False
        else:
            screen.blit(self.images[(tick-self.time_of_spawn)//(self.duration//self.imagecount)-1], (self.x, self.y))
