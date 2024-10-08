from pygame.font import Font
from sprite import Sprite
import pygame
import config
import keybind
from ui.element import UIElement
from ui.text import Text
import images
from typing import Callable

class Button(UIElement):
    def __init__(self, sprite: Sprite|None = Sprite(images.ui.button_image), x: int = 0, y: int = 0, content: str = "", font_size: int = config.cfg.ui.font_size, center_font: bool = True, base_color: pygame.color.Color = "0xAAAAAA", click_color: pygame.color.Color = "0xFFFFFF", hover_color: pygame.color.Color = "0x00FFFF", on_click: Callable|tuple|None = None, on_hover: Callable|tuple|None = None, on_rclick: Callable|tuple|None = None,id: str = ""):
        super().__init__(id)
        self.sprite = sprite
        self.x, self.y = x, y
        self.center_font = center_font
        self.font_size = font_size
        self.base_color, self.click_color, self.hover_color = base_color, click_color, hover_color

        if isinstance(on_click, Callable): # on_click is either a function or a tuple containing a function and args
            self.on_click = (on_click,) # make tuple with no args
        else:
            self.on_click = on_click

        if isinstance(on_hover, Callable):
            self.on_hover = (on_hover,)
        else:
            self.on_hover = on_hover

        if isinstance(on_rclick, Callable):
            self.on_rclick = (on_rclick,)
        else:
            self.on_rclick = on_rclick

        self.set_text(content)

        if self.sprite is None:
            self.sprite = self.text

    def update(self, screen, mouse_x, mouse_y, click: bool = False, release: bool = False, rclick: bool = False, rrelease: bool = False, **kwargs):
        super().update(**kwargs)
        # Check for mouse collision
        if self.x + self.sprite.size[0] >= mouse_x >= self.x and self.y + self.sprite.size[1] >= mouse_y >= self.y:
            if (rclick and self.on_rclick) or click: # only highlight on rclick if self.on_rclick is set
                self.set_color(self.click_color)
            elif release: # Buttons activate when mouse is released, not pressed
                if self.on_click: self.on_click[0](*self.on_click[1:]) # call with args
            elif rrelease:
                if self.on_rclick: self.on_rclick[0](*self.on_rclick[1:])
            else: # hover
                self.set_color(self.hover_color)
                if self.on_hover: self.on_hover[0](*self.on_hover[1:])
        else:
            self.set_color(self.base_color)

        if self.sprite is not None:
            self.sprite.draw(screen, self.x, self.y)

        self.text.update(screen)

    def set_text(self, content: str):
        if self.center_font:
            self.text = Text(content, self.x + self.sprite.size[0] // 2, self.y + self.sprite.size[1] // 2, self.base_color, size=self.font_size, center=True)
        else:
            self.text = Text(content, self.x + 10, self.y + 10, self.base_color, size=self.font_size, center=False)

    def set_color(self, color: pygame.Color):
        self.text.set_color(color)

class ConfigOption(Button):
    def __init__(self, cfg: config.Config, category: str, key: str, sprite: Sprite | None = Sprite(images.ui.narrow_button_image), font_size: int = config.cfg.ui.narrow_font_size, is_keybind: bool = False, **kwargs):
        super().__init__(sprite, on_click=self.update_config_option, on_rclick=(self.update_config_option, True), font_size=font_size, center_font=False, **kwargs)

        self.config = cfg
        self.category = category
        self.key = key
        value = self.config.d[self.category][self.key]

        if is_keybind: self.type = 5
        elif isinstance(value, bool): self.type = 1
        elif isinstance(value, int): self.type = 2
        elif isinstance(value, float): self.type = 3
        elif isinstance(value, str): self.type = 4
        else: self.type = 0

    def update(self, screen, mouse_x, mouse_y, click: bool = False, release: bool = False, no_set_text: bool = False, **kwargs):
        if not no_set_text:
            self.screen = screen
            if self.type == 5: # keybind
                self.set_text(f"{self.key}: {keybind.keymap.get(str(self.config.d[self.category][self.key]))}")
            else:
                self.set_text(f"{self.key}: {self.config.d[self.category][self.key]}")
        return super().update(screen, mouse_x, mouse_y, click, release, **kwargs)
    
    def enter_text(self):
        pygame.key.start_text_input()
        new_text = ""
        while True:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    try: new_text = new_text[:-1]
                    except: pass

                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) or keybind.is_pressed(event, config.kb.other.quit):
                    try:
                        match self.type:
                            case 2: self.config.set_value(self.category, self.key, int(new_text))
                            case 3: self.config.set_value(self.category, self.key, float(new_text))
                            case 4: self.config.set_value(self.category, self.key, str(new_text))
                    except: pass
                    finally:
                        pygame.key.stop_text_input() 
                        break

            elif event.type == pygame.TEXTINPUT:
                new_text += event.text
            
            self.set_text(f"{self.key}: {new_text}_")
            self.update(self.screen, mouse_x=0, mouse_y=0, no_set_text=True)
            pygame.display.update()
                

    def update_config_option(self, right: bool = False):
        value = self.config.d[self.category][self.key]

        if right: # right-click
            match self.type:
                case 1: self.config.toggle_value(self.category, self.key)
                case 4: self.config.set_value(self.category, self.key, "")

        else: # left-click
            if self.type == 1: self.config.toggle_value(self.category, self.key)
            elif self.type in (2,3,4): self.enter_text()
            elif self.type == 5:
                while True:
                    self.set_text(f"{self.key}: _")
                    self.update(self.screen, mouse_x=0, mouse_y=0, no_set_text=True)
                    pygame.display.update()
                    event = pygame.event.wait()
                    if event.type == pygame.KEYDOWN:
                        if event.key == config.kb.other.quit: break
                        self.config.set_value(self.category, self.key, event.key)
                        break

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.config.set_value(self.category, self.key, event.button+1024)
                        break
