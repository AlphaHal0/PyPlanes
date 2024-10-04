from ui.element import UIElement
import pygame
from config import cfg
from display import screen

class Text(UIElement):
    """Class to represent a rendered font"""
    def  __init__(self, content: str = "", color: pygame.Color = 0, size: int = 0, center: bool = False, width: int = 0, height: int = 0, **kwargs):
        super().__init__(**kwargs)
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
        if center:
            self.x_adg = self.x - self.width // 2
            self.y_adg = self.y - self.height // 2
        else:
            self.x_adg, self.y_adg = self.x, self.y

    def update(self, **kwargs):
        """Draw on screen"""
        if cfg.debug.show_sprite_sizes:
            pygame.draw.rect(screen.surface, (0, 255, 255), ((self.x_adg, self.y_adg), (self.width, self.height)))
            pygame.draw.circle(screen.surface, (0, 0, 255), (self.x, self.y), 5)
        screen.surface.blit(self.render, (self.x_adg, self.y_adg))
        return super().update(**kwargs)

    def reload(self):
        """Re-render font"""
        self.render = self.font.render(self.content, False, self.color)
        if self.width == 0 or self.height == 0:
            self.rect = self.render.get_rect()
            self.width = self.rect.width
            self.height = self.rect.height
        if self.center:
            self.x_adg = self.x - self.rect.width // 2
            self.y_adg = self.y - self.rect.height // 2
    
    def set_color(self, color: pygame.Color):
        """Set font colour"""
        if color == self.color: return
        self.color = color
        self.reload()

    def set_content(self, content: str):
        """Set font content"""
        if content == self.content: return
        self.content = content
        self.reload()

    def set_size(self, size: int):
        """Set font size"""
        if size == self.size: return
        self.font = pygame.font.Font(size=size)
        self.size = size
        self.reload()
