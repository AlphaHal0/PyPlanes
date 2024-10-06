import pygame
from config import cfg

class Texture:
    """(WIP) Class that represents either a pygame Surface or an ID for a GL texture"""
    def __init__(self, image: pygame.Surface | int, size: tuple) -> None:
        self.image = image
        self.size = size
        if cfg.opengl:
            self.type = 1
        else:
            self.type = 0
