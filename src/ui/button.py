from pygame.font import Font
from sprite import Sprite
import pygame
import config
from ui.element import UIElement
from ui.text import Text
import images
from typing import Callable

class Button(UIElement):
    def __init__(self, sprite: Sprite|None = Sprite(images.ui.button_image), x: int = 0, y: int = 0, content: str = "", font: pygame.font.Font = pygame.font.get_default_font(), base_color: pygame.color.Color = 0xD7FCD4, click_color: pygame.color.Color = 0xFFFFFF, hover_color: pygame.color.Color = 0xD8D8D8, on_click: Callable|tuple|None = None, on_hover: Callable|tuple|None = None, id: str = ""):
        super().__init__(id)
        self.sprite = sprite
        self.x, self.y = x, y
        self.font = font
        self.base_color, self.click_color, self.hover_color = base_color, click_color, hover_color

        if isinstance(on_click, Callable): # on_click is either a function or a tuple containing a function and args
            self.on_click = (on_click,) # make tuple with no args
        else:
            self.on_click = on_click

        if isinstance(on_hover, Callable):
            self.on_hover = (on_hover,)
        else:
            self.on_hover = on_hover

        self.text = Text(content, x, y, base_color)
        if self.sprite is None:
            self.sprite = self.text

    def update(self, screen, mouse_x, mouse_y, click: bool = False, release: bool = False, **kwargs):
        super().update(**kwargs)
        # Check for mouse collision
        if self.x + self.sprite.size[0] >= mouse_x >= self.x and self.y + self.sprite.size[1] >= mouse_y >= self.y:
            if click: # click
                self.set_color(self.click_color)
            elif release: # Buttons activate when mouse is released, not pressed
                self.set_color(self.base_color)
                if self.on_click: 
                    self.on_click[0](*self.on_click[1:]) # call with args
            else: # hover
                self.set_color(self.hover_color)
                if self.on_hover:
                    self.on_hover[0](*self.on_hover[1:])

        if self.sprite is not None:
            self.sprite.draw(screen, self.x, self.y)

        self.text.update(screen)

    def set_color(self, color: pygame.Color):
        self.text.set_color(color)

class ConfigButton(Button):
    def __init__(self, cfg: config.Config, category: str, key: str, sprite: Sprite | None = Sprite(images.ui.narrow_button_image), x: int = 0, y: int = 0, font: Font = pygame.font.get_default_font(), base_color: pygame.Color = 14154964, click_color: pygame.Color = 16777215, hover_color: pygame.Color = 14211288, id: str = ""):
        super().__init__(sprite, x, y, None, font, base_color, click_color, hover_color, self.update_config_option, id=id)
        self.config = cfg
        self.category = category
        self.key = key
        self.text.set_content(f"{self.key}: {self.config.d[self.category][self.key]}")

    def update(self, screen, mouse_x, mouse_y, click: bool = False, release: bool = False, **kwargs):
        self.text.set_content(f"{self.key}: {self.config.d[self.category][self.key]}")
        return super().update(screen, mouse_x, mouse_y, click, release, **kwargs)

    def update_config_option(self):
        self.config.toggle_value(self.category, self.key)
