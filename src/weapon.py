from entity import Entity
from images import im
from random import random
from particle import Particle
from sprite import Sprite
from config import cfg

class Weapon(Entity):
    """A class to represent any weapon, usually initiated by an Aircraft"""
    def __init__(self, is_enemy: bool = False, explosion_power: int = 0, **kwargs):
        super().__init__(**kwargs)
        if is_enemy:
            self.sprite.flip(no_update=False)
        self.is_enemy = is_enemy
        self.explosion_power = explosion_power

    def is_colliding_entity(self, other: Entity, ignore_same_team: bool = True) -> bool:
        """Checks if colliding with another Entity.
        If ignore_same_team is True, does not collide with same-team bullets"""
        if ignore_same_team and self.is_enemy == other.is_enemy:
            return False
        
        return super().is_colliding(other.rect)
    
    def explode(self, entities: list = []) -> Particle:
        """Destroys self and returns a Particle.
        If entities is given, runs Entity.fall() if it is in the blast radius given by self.explosion_power."""
        self.destroy()

        if self.explosion_power:
            for i in entities:
                if i.distance_to(self.x, self.y) < self.explosion_power * 30:
                    i.fall()
            return Particle(self.x, self.y, sprite=Sprite(im.particle.large_explosions, size_multiplier=self.explosion_power), duration=20 * self.explosion_power)
        else:
            return Particle(self.x, self.y, sprite=Sprite(im.particle.small_explosions), duration=10)

class Bullet(Weapon):
    """A Weapon that represents a bullet"""
    def __init__(self, sprite: Sprite|None = None, velocity_x: int = cfg.physics.enemy_bullet_velocity, is_enemy: bool = False, **kwargs):
        if sprite is None: sprite = Sprite(im.weapons.bullet, animation_time=5)
        super().__init__(sprite=sprite, velocity_x=-velocity_x if is_enemy else velocity_x, is_enemy=is_enemy, **kwargs)

class Bomb(Weapon):
    """A Weapon that represents a bomb"""
    def __init__(self, sprite: Sprite|None = None, velocity_x: int = 5, velocity_y: int = 0, drag_multiplier: float = 0.1, is_enemy: bool = False, **kwargs):
        if sprite is None: sprite = Sprite(im.weapons.bomb)
        if random() <= cfg.easter_eggs.berry_bomb_chance:
            sprite = Sprite(im.weapons.blueberry)
        super().__init__(sprite=sprite, velocity_x=-velocity_x if is_enemy else velocity_x, velocity_y=velocity_y + cfg.physics.bomb_y_velocity_gain, is_enemy=is_enemy, **kwargs)
        self.drag_multiplier = drag_multiplier
        
    def update(self):
        """Updates this Bomb.
        Gradually slows down on the X axis to zero.
        Gradually speeds up on the Y axis."""
        super().update()
        self.velocity_x -= cfg.physics.bomb_x_velocity_decay // (1 + self.velocity_x * self.drag_multiplier)
        self.velocity_y += cfg.physics.bomb_y_velocity_gain * (1 + self.velocity_y / cfg.physics.bomb_terminal_velocity)
