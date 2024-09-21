from config import cfg
import pygame

sz = cfg.sprite_sizes

def load_image(file: str):
    return pygame.image.load(f"{cfg.asset_folder}/{file}").convert_alpha()

def scale_image(surface: pygame.Surface, size: list|float, relative: bool = True):
    if relative:
        if isinstance(size, list):
            return pygame.transform.scale(surface, (size[0] * cfg.screen_width, size[1] * cfg.screen_height))
        else:
            size *= cfg.screen_height
            return pygame.transform.scale(surface, (size*(surface.get_width()/surface.get_height()), size))
    else:
        return pygame.transform.scale(surface, size)

def flip_image(surface: pygame.Surface, flip_x: bool = True, flip_y: bool = False):
    return pygame.transform.flip(surface, flip_x, flip_y)

bullet_image = load_image("weapons/bullets/Shot1.png")
bullet_image = scale_image(bullet_image, sz['bullet_image'])

background_image = scale_image(load_image("sky/side-scroll.jpg"), sz['background_image'])

aircraft_image = scale_image(load_image("planes/player/spitfire.png"), sz['aircraft_image'])
enemy_image = scale_image(load_image("planes/enemies/enemy_lvl_1.png"), sz['enemy_image'])

large_explosions = []
for i in range(4):
    large_explosions.append(
        scale_image(load_image(f"particle/fire/large-{i+1}.png"), sz['large_explosions']))

small_explosions = []
for i in range(4):
    small_explosions.append(
        scale_image(load_image(f"particle/smoke/large-{i+1}.png"), sz['small_explosions']))
    
moth_images = []
for i in range(8):
    moth_images.append(
        scale_image(load_image(f"easteregg/moth/frame_{i}.png"), sz['moth_images']))

bomb_image = flip_image(scale_image(load_image("weapons/bombs/British/GP-1000lb-MK-IV.png"), sz['bomb_image']))

blueberry = scale_image(load_image("easteregg/blueberry.png"), sz['blueberry'])
