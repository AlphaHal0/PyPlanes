from entity import Entity
import pygame
import images
from particle import Particle
from constants import BULLET_VELOCITY, BOMB_Y_VELOCITY_GAIN, BOMB_X_VELOCITY_DECAY, BOMB_TERMINAL_VELOCITY

class Weapon(Entity):
    def __init__(self, x: int = 0, y: int = 0, image: pygame.Surface|None = None, is_enemy: bool = False, explosion_power: int = 0, velocity_x: int = 0, velocity_y: int = 0):
        image = image
        if is_enemy:
            image = pygame.transform.flip(image, True, False)
        rect = image.get_rect(topleft=(x, y))
        self.is_enemy = is_enemy
        self.x = x
        self.y = y
        self.explosion_power = explosion_power

        super().__init__(rect, 0, image, x, y, velocity_x, velocity_y)

    def is_colliding_entity(self, other: Entity, ignore_same_team: bool = True) -> bool:
        # Do not collide with same-team bullets
        if ignore_same_team and self.is_enemy == other.is_enemy:
            return False
        
        return super().is_colliding(other.rect)
    
    def explode(self) -> Particle:
        self.destroy()

        if self.explosion_power:
            return Particle(self.x, self.y, images=images.large_explosions, duration=200 * self.explosion_power, scale=self.explosion_power)
        else:
            return Particle(self.x, self.y, images=images.small_explosions, duration=100)

class Bullet(Weapon):
    def __init__(self, x: int, y: int, is_enemy: bool = False, velocity_x: int = BULLET_VELOCITY, velocity_y: int = 0):
        super().__init__(x, y, images.bullet_image, is_enemy, 0, -velocity_x if is_enemy else velocity_x, velocity_y)

class Bomb(Weapon):
    def __init__(self, x: int, y: int, is_enemy: bool = False, velocity_x: int = 5, velocity_y: int = 0, drag_multiplier: float = 0.1, explosion_power: int = 0):
        super().__init__(x, y, images.bomb_image, is_enemy, explosion_power, velocity_x, velocity_y + BOMB_Y_VELOCITY_GAIN)
        self.drag_multiplier = drag_multiplier
        
    def update_position(self):
        super().update_position()
        self.velocity_x -= BOMB_X_VELOCITY_DECAY // (1 + self.velocity_x * self.drag_multiplier)
        self.velocity_y += BOMB_Y_VELOCITY_GAIN * (1 + self.velocity_y / BOMB_TERMINAL_VELOCITY)
