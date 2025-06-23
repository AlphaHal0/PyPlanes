# To Create ENV: py -m venv env
# To Enter ENV: env/scripts/activate.ps1
import pygame
from config import cfg, kb

from ui.button import Button, ConfigOption
from ui.menu import Menu, ALIGN_LEFT, ALIGN_NONE
from ui.text import Text
from sprite import Sprite
from images import im, image_toc
from game import play

def finish():
    """Exit game and save config"""
    pygame.quit()
    cfg.save()
    kb.save()
    quit()

options_menu = None

def options(con = cfg, is_keybind: bool = False):
    """Options menu handler.
    Creates and manages a ui.menu.Menu for the con arg.
    If is_keybind, buttons will be set to manage keybinds"""
    categories = list(con.d.keys())
    def refresh(page = 0, reset_confirm = 0, close = False): # TODO: function function ambiguous. TODO message also ambiguous. fix.
        global options_menu # TODO: remove global

        if options_menu: options_menu.run = False
        if close:
            return
        elements = []
        if len(con.d) < 1:
            elements.append(Text("This configuration has no options.", grid_pos=(0, 0), color="0xFFFFFF", size=40))
        else:
            category = categories[page]
            elements.append(Text(f"Page {page+1}/{len(con.d)}", grid_pos=(0, 0), color="0xFFFFFF", size=40))
            elements.append(Text(category.replace('_', ' ').capitalize(), grid_pos=(0, 1), color="0xFFFFFF", size=40))
            i = 2
            x = 0
            for key, value in con.d[category].items():
                if i > 12:
                    i = 2
                    x += 1
                elements.append(ConfigOption(cfg=con, category=category, key=key, grid_pos=(x, i), is_keybind=is_keybind))
                i += 1

        if page > 0: elements.append(Button(sprite=Sprite(im.ui.small_button), font_size=cfg.ui.narrow_font_size, content="<--", base_color="0xFFFF00", on_click=(refresh, page-1), grid_pos=(3, 14)))
        if page < len(con.d)-1: elements.append(Button(sprite=Sprite(im.ui.small_button), font_size=cfg.ui.narrow_font_size, content="-->", base_color="0xFFFF00", on_click=(refresh, page+1), grid_pos=(3.47, 14)))
        if reset_confirm == 1:
            elements.append(Button(sprite=Sprite(im.ui.narrow_button), font_size=cfg.ui.narrow_font_size, content="Confirm reset", base_color="0xFF0000", on_click=(refresh, page, 2), grid_pos=(3, 15)))
        elif reset_confirm == 2:
            con.reset()
            refresh(page)
            return
        else:
            elements.append(Button(sprite=Sprite(im.ui.narrow_button), font_size=cfg.ui.narrow_font_size, content="Reset to defaults", base_color="0xFF4444", on_click=(refresh, page, 1), grid_pos=(3, 15)))

        elements.append(Button(sprite=Sprite(im.ui.narrow_button), font_size=cfg.ui.narrow_font_size, content="Back to Menu", base_color="0xAAAAAA", on_click=(refresh, page, 0, True), grid_pos=(0, 15)))

        options_menu = Menu(
            Sprite(im.ui.background),
            elements=elements,
            grid_type=ALIGN_LEFT
        )

        options_menu.loop()

    refresh()

def keybinds():
    options(kb, is_keybind=True)

def start_game(): play()

def main():
    """Main loop"""

    # play menu music (synth noodles)
    pygame.mixer.music.load(f"./res/audio/intro.ogg", "music_menu")
    pygame.mixer.music.play(1)

    button_pos = cfg.screen_width // 2 - image_toc.ui.button['scale'][0] * cfg.screen_width // 2
    main_menu = Menu(
        Sprite(im.ui.background),
        elements=[
            Text("PyPlanes", x=cfg.screen_width // 2, y=cfg.screen_height // 8 + 50, color="0xFFFFFF", center=True, size=cfg.screen_height // 10),
            Button(x=button_pos, y=2 * cfg.screen_height // 8 + 50, content="PLAY", on_click=start_game),
            Button(x=button_pos, y=3 * cfg.screen_height // 8 + 50, content="OPTIONS", on_click=options),
            Button(x=button_pos, y=4 * cfg.screen_height // 8 + 50, content="KEYBINDS", on_click=keybinds),
            Button(x=button_pos, y=6 * cfg.screen_height // 8 + 50, content="QUIT", on_click=finish),
        ],
        on_close=finish,
        grid_type=ALIGN_NONE
    )

    main_menu.loop()

main()
finish()
