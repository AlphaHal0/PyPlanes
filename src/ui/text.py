from ui.element import UIElement
import pygame

class Text(UIElement):
    def  __init__(self, content: str = "", x: int = 0, y: int = 0, color: pygame.Color = 0, id: str = "", size: int = 30):
        self.content = content
        self.color = color
        self.x, self.y = x, y
        self.size = size
        self.font = pygame.font.Font(size=size)
        self.render = self.font.render(content, False, color)
        super().__init__(id)

    def update(self, screen: pygame.Surface, **kwargs):
        screen.blit(self.render, (self.x, self.y))
        return super().update(**kwargs)

    def reload(self):
        self.render = self.font.render(self.content, False, self.color)
    
    def set_color(self, color: pygame.Color):
        self.color = color
        self.reload()

    def set_content(self, content: str):
        self.content = content
        self.reload()

    def set_size(self, size: int):
        self.font = pygame.font.Font(size=size)
        self.size = size
        self.reload()
