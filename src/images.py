from config import cfg
import pygame

sz = cfg.sprite_sizes
ui_sz = cfg.ui

def load_image(file: str) -> pygame.Surface:
    """Loads an image from file and returns a pygame.Surface.
    Checks `./mod/res/img/{file}` first, then `./res/img/{file}`.
    """
    try:
        return pygame.image.load(f"./mod/res/img/{file}").convert_alpha()
    except FileNotFoundError:
        return pygame.image.load(f"./res/img/{file}").convert_alpha()

def scale_image(surface: pygame.Surface, size: list|float, relative: bool = True) -> pygame.Surface:
    """Returns a scaled pygame.Surface by size.
    If relative is True, the surface is scaled as a fraction of the screen size.
    e.g. 0.1 returns a Surface that is 0.1 times the screen height
    and [0.1, 0.2] returns a Surface that is 0.1x height and 0.2x width."""
    if relative:
        if isinstance(size, list):
            return pygame.transform.scale(surface, (size[0] * cfg.screen_width, size[1] * cfg.screen_height))
        else:
            size *= cfg.screen_height
            return pygame.transform.scale(surface, (size*(surface.get_width()/surface.get_height()), size))
    else:
        return pygame.transform.scale(surface, size)

def flip_image(surface: pygame.Surface, flip_x: bool = True, flip_y: bool = False):
    """Flips a pygame.Surface"""
    return pygame.transform.flip(surface, flip_x, flip_y)

bullet_image = scale_image(load_image("weapons/bullets/Shot1.png"), sz.bullet_image)

background_image = scale_image(load_image("sky/side-scroll.jpg"), sz.background_image)

class ui:
    """UI image class"""
    menu_background_image = scale_image(load_image(f"ui/background.png"), sz.background_image)
    button_image = scale_image(load_image(f"ui/button.png"), ui_sz.button_size)
    narrow_button_image = scale_image(load_image(f"ui/button.png"), ui_sz.narrow_button_size)
    small_button_image = scale_image(load_image(f"ui/button.png"), ui_sz.small_button_size)

aircraft_image = scale_image(load_image("planes/player/spitfire.png"), sz.aircraft_image)

enemy_1_image = scale_image(load_image("planes/enemies/enemy_lvl_1.png"), sz.enemy_image)
enemy_2_image = scale_image(load_image("planes/enemies/enemy_lvl_2.png"), sz.enemy_image)
enemy_3_image = scale_image(load_image("planes/enemies/enemy_lvl_3.png"), sz.enemy_image)
enemy_4_image = scale_image(load_image("planes/enemies/enemy_lvl_4.png"), sz.enemy_image)
enemy_5_image = scale_image(load_image("planes/enemies/enemy_lvl_5.png"), sz.enemy_image)

large_explosions = []
for i in range(4):
    large_explosions.append(
        scale_image(load_image(f"particle/fire/large-{i+1}.png"), sz.large_explosions))

small_explosions = []
for i in range(4):
    small_explosions.append(
        scale_image(load_image(f"particle/smoke/large-{i+1}.png"), sz.small_explosions))
    
moth_images = []
for i in range(8):
    moth_images.append(
        scale_image(load_image(f"easteregg/moth/frame_{i}.png"), sz.moth_images))

bomb_image = flip_image(scale_image(load_image("weapons/bombs/British/GP-1000lb-MK-IV.png"), sz.bomb_image))

blueberry = scale_image(load_image("easteregg/blueberry.png"), sz.blueberry)
