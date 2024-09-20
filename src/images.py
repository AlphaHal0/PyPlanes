from config import cfg
from pygame import image, transform, surface

def load_image(file: str):
    return image.load(f"{cfg.asset_folder}/{file}").convert_alpha()

def scale_image(surface: surface, size: tuple):
    return transform.scale(surface, size)

def flip_image(surface: surface, flip_x: bool = True, flip_y: bool = False):
    return transform.flip(surface, flip_x, flip_y)

bullet_image = load_image("weapons/bullets/Shot1.png")
bullet_image = scale_image(bullet_image, (bullet_image.get_width() * 3, bullet_image.get_height() * 3))

background_image = scale_image(load_image("sky/side-scroll.jpg"), (cfg.screen_width, cfg.screen_height))

aircraft_image = scale_image(load_image("planes/player/spitfire.png"),(cfg.screen_width / 10, cfg.screen_height / 20))
enemy_image = scale_image(load_image("planes/enemies/enemy_lvl_1.png"),(cfg.screen_width / 10, cfg.screen_height / 20))

large_explosions = []
for i in range(4):
    large_explosions.append(
        scale_image(load_image(f"particle/fire/large-{i+1}.png"), (50, 50)))

small_explosions = []
for i in range(4):
    small_explosions.append(
        scale_image(load_image(f"particle/smoke/large-{i+1}.png"), (50, 50)))
    
moth_images = []
for i in range(8):
    moth_images.append(
        scale_image(load_image(f"easteregg/moth/frame_{i}.png"), (cfg.screen_height / 15, cfg.screen_height / 15)))

bomb_image = flip_image(scale_image(load_image("weapons/bombs/British/GP-1000lb-MK-IV.png"), (74, 18)))

blueberry = scale_image(load_image("easteregg/blueberry.png"), (50, 50))
