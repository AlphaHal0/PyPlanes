# To Create ENV: py -m venv env
# To Enter ENV: env/scripts/activate.ps1
import pygame
from config import cfg, kb

# Initialize Pygame
pygame.init()
pygame.font.init()

font = pygame.font.Font(size=50)
# Set up the screen
screen = pygame.display.set_mode((cfg.screen_width, cfg.screen_height))

from ui.button import Button, ConfigOption
from ui.menu import Menu
from ui.text import Text
from sprite import Sprite
import images as im
from game import play

def finish():
    pygame.quit()
    cfg.save()
    kb.save()
    quit()

def options():
    elements = []
    i = 0
    x = 0
    for category, contents in cfg.d.items():
        if i > 14:
            i = 0
            x += 1
        elements.append(Text(category, y=i*(cfg.screen_height//16)+20, x=x*(cfg.screen_width//4)+20, color="0xFFFFFF", size=40))
        i += 1
        for key, value in contents.items():
            if i > 14:
                i = 0
                x += 1
            elements.append(ConfigOption(cfg=cfg, category=category, key=key, y=i*(cfg.screen_height//16)+20, x=x*(cfg.screen_width//4)+20))
            i += 1
            

    elements.append(Button(sprite=Sprite(im.ui.narrow_button_image), font_size=cfg.ui.narrow_font_size, content="Reset to defaults", base_color="0xFF0000", on_click=cfg.reset, y=14*(cfg.screen_height//16)+20, x=3*(cfg.screen_width//4)+20))

    options_menu = Menu(
        Sprite(im.ui.menu_background_image),
        elements=elements
    )

    options_menu.loop(screen)

def keybinds():
    elements = []
    i = 0
    x = 0
    for category, contents in kb.d.items():
        if i > 14:
            i = 0
            x += 1
        elements.append(Text(category, y=i*(cfg.screen_height//16)+20, x=x*(cfg.screen_width//4)+20, color="0xFFFFFF", size=40))
        i += 1
        for key, value in contents.items():
            if i > 14:
                i = 0
                x += 1
            elements.append(ConfigOption(cfg=kb, category=category, key=key, y=i*(cfg.screen_height//16)+20, x=x*(cfg.screen_width//4)+20, is_keybind=True))
            i += 1

    elements.append(Button(sprite=Sprite(im.ui.narrow_button_image), font_size=cfg.ui.narrow_font_size, content="Reset to defaults", base_color="0xFF0000", on_click=kb.reset, y=14*(cfg.screen_height//16)+20, x=3*(cfg.screen_width//4)+20))

    options_menu = Menu(
        Sprite(im.ui.menu_background_image),
        elements=elements
    )
    
    options_menu.loop(screen)

def start_game(): play(screen, font)

def main():
    button_pos = cfg.screen_width // 2 - cfg.ui.button_size[0] * cfg.screen_width // 2
    main_menu = Menu(
        Sprite(im.ui.menu_background_image),
        elements=[
            Text("MAIN MENU", cfg.screen_width // 2, 100, color="0xFFFFFF", center=True),
            Button(x=button_pos, y=250, content="PLAY", on_click=start_game),
            Button(x=button_pos, y=350, content="OPTIONS", on_click=options),
            Button(x=button_pos, y=450, content="KEYBINDS", on_click=keybinds),
            Button(x=button_pos, y=650, content="QUIT", on_click=finish),
        ],
        on_quit=finish
    )

    main_menu.loop(screen)

main()
finish()
