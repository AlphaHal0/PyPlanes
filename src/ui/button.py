from sprite import Sprite
import pygame
from ui.element import UIElement

class Button(UIElement):
    def __init__(self, sprite: Sprite|None = None, x: int = 0, y: int = 0, text_input: str = "", font: pygame.font.Font = pygame.font.get_default_font(), base_color: pygame.color.Color = 0xD7FCD4, click_color: pygame.color.Color = 0xFFFFFF, hover_color: pygame.color.Color = 0xD8D8D8, on_click: function|None = None, on_hover: function|None = None, id: str = ""):
        super().__init__(id)
        self.sprite = sprite
        self.x, self.y = x, y
        self.font = font
        self.base_color, self.click_color, self.hover_color = base_color, click_color, hover_color
        self.text_input = text_input
        self.on_click, self.on_hover = on_click, on_hover
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.sprite is None:
            self.sprite = self.text
        self.text_rect = self.text.get_rect(center=(self.x, self.y))

    def update(self, screen, mouse_x, mouse_y, click: bool = False, release: bool = False):
        super().update()
        # Check for mouse collision
        if mouse_x in range(self.rect.left, self.rect.right) and mouse_y in range(self.rect.top, self.rect.bottom):
            if click: # click
                self.set_color(self.click_color)
            elif release: # Buttons activate when mouse is released, not pressed
                self.set_color(self.base_color)
                if self.on_click: self.on_click()
            else: # hover
                self.set_color(self.hover_color)
                if self.on_hover: self.on_hover()

        if self.sprite is not None:
            self.sprite.draw(screen, self.x, self.y)
        screen.blit(self.text, self.text_rect)

    def set_color(self, color: pygame.Color):
        self.text = self.font.render(self.text_input, True, color)