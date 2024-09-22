from ui.element import UIElement
import pygame
from config import cfg

class Text(UIElement):
    def  __init__(self, content: str = "", x: int = 0, y: int = 0, color: pygame.Color = 0, size: int = 0, center: bool = False, width: int = 0, height: int = 0, id: str = ""):
        if size == 0: size = cfg.ui.font_size
        self.content = content
        self.color = color
        self.size = size
        self.font = pygame.font.Font(size=size)
        self.render = self.font.render(content, False, color)
        self.center = center
        if width == 0 or height == 0:
            self.rect = self.render.get_rect()
            self.width = self.rect.width
            self.height = self.rect.height
        self.x, self.y = x, y
        if center:
            self.x_adg = x - self.width // 2
            self.y_adg = y - self.height // 2
        else:
            self.x_adg, self.y_adg = x, y
        super().__init__(id)

    def update(self, screen: pygame.Surface, **kwargs):
        if cfg.debug.show_sprite_sizes:
            pygame.draw.rect(screen, (0, 255, 255), ((self.x_adg, self.y_adg), (self.width, self.height)))
            pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), 5)
        screen.blit(self.render, (self.x_adg, self.y_adg))
        return super().update(**kwargs)

    def reload(self):
        self.render = self.font.render(self.content, False, self.color)
        if self.width == 0 or self.height == 0:
            self.rect = self.render.get_rect()
            self.width = self.rect.width
            self.height = self.rect.height
        if self.center:
            self.x_adg = self.x - self.rect.width // 2
            self.y_adg = self.y - self.rect.height // 2
    
    def set_color(self, color: pygame.Color):
        if color == self.color: return
        self.color = color
        self.reload()

    def set_content(self, content: str):
        if content == self.content: return
        self.content = content
        self.reload()

    def set_size(self, size: int):
        if size == self.size: return
        self.font = pygame.font.Font(size=size)
        self.size = size
        self.reload()
