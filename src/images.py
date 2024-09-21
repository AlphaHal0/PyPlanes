from config import cfg
import pygame

def load_image(file: str):
    return pygame.image.load(f"{cfg.asset_folder}/{file}").convert_alpha()

def scale_image(surface: pygame.Surface, size: tuple|float, relative: bool = True):
    if relative:
        if isinstance(size, tuple):
            return pygame.transform.scale(surface, (size[0] * cfg.screen_width, size[1] * cfg.screen_height))
        else:
            size *= cfg.screen_height
            return pygame.transform.scale(surface, (size*(surface.get_width()/surface.get_height()), size))
    else:
        return pygame.transform.scale(surface, size)

def flip_image(surface: pygame.Surface, flip_x: bool = True, flip_y: bool = False):
    return pygame.transform.flip(surface, flip_x, flip_y)

bullet_image = load_image("weapons/bullets/Shot1.png")
bullet_image = scale_image(bullet_image, 0.025)

background_image = scale_image(load_image("sky/side-scroll.jpg"), (1, 1))

aircraft_image = scale_image(load_image("planes/player/spitfire.png"), 0.05)
enemy_image = scale_image(load_image("planes/enemies/enemy_lvl_1.png"), 0.05)

large_explosions = []
for i in range(4):
    large_explosions.append(
        scale_image(load_image(f"particle/fire/large-{i+1}.png"), 0.05))

small_explosions = []
for i in range(4):
    small_explosions.append(
        scale_image(load_image(f"particle/smoke/large-{i+1}.png"), 0.0625))
    
moth_images = []
for i in range(8):
    moth_images.append(
        scale_image(load_image(f"easteregg/moth/frame_{i}.png"), 0.0667))

bomb_image = flip_image(scale_image(load_image("weapons/bombs/British/GP-1000lb-MK-IV.png"), 0.025))

blueberry = scale_image(load_image("easteregg/blueberry.png"), 0.0625)
