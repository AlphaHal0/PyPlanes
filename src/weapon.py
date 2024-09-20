from entity import Entity
import pygame
import images
from constants import BULLET_VELOCITY, BOMB_Y_VELOCITY_GAIN, BOMB_X_VELOCITY_DECAY, BOMB_TERMINAL_VELOCITY

class Weapon(Entity):
    def __init__(self, x, y, image: pygame.Surface, is_enemy: bool = False, explosion_power: int = 0):
        image = image
        if is_enemy:
            image = pygame.transform.flip(image, True, False)
        rect = image.get_rect(topleft=(x, y))
        self.is_enemy = is_enemy
        self.x = x
        self.y = y
        self.explosion_power = explosion_power

        super().__init__(rect, 0, image)

    def is_colliding_entity(self, other: Entity, ignore_same_team: bool = True):
        # Do not collide with same-team bullets
        if ignore_same_team and self.is_enemy == other.is_enemy:
            return False
        
        return super().is_colliding(other.rect)

class Bullet(Weapon):
    def __init__(self, x, y, is_enemy = False, velocity = BULLET_VELOCITY):
        super().__init__(x, y, images.bullet_image, is_enemy)

        if is_enemy:
            self.velocity = -velocity
        else:
            self.velocity = velocity

    def update_position(self):
        self.rect.move_ip(self.velocity, 0)
        self.x += self.velocity

class Bomb(Weapon):
    def __init__(self, x, y, is_enemy = False, velocity_y = 0, velocity_x = 5, drag_multiplier = 0.1, explosion_power = 1):
        super().__init__(x, y, images.bomb_image, is_enemy, explosion_power)
        self.velocity_y = velocity_y + BOMB_Y_VELOCITY_GAIN
        self.velocity_x = velocity_x
        self.drag_multiplier = drag_multiplier
        
    def update_position(self):
        self.rect.move_ip(self.velocity_x, self.velocity_y)
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_x -= BOMB_X_VELOCITY_DECAY // (self.velocity_x * self.drag_multiplier)
        self.velocity_y += BOMB_Y_VELOCITY_GAIN * (1 + self.velocity_y / BOMB_TERMINAL_VELOCITY)
