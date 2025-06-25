from entity import Entity
from images import im
from random import random
from particle import Particle
from sprite import Sprite
from vehicle import Vehicle
import collision
from config import cfg

class Weapon(Entity):
    """A class to represent any weapon, usually initiated by an Aircraft"""
    def __init__(self, is_enemy: bool = False, explosion_power: int = 0, **kwargs):
        super().__init__(**kwargs)
        if is_enemy:
            self.sprite.flip(no_update=False)
        self.is_enemy = is_enemy
        self.explosion_power = explosion_power

    def explode(self, entities: list = []) -> Particle:
        """Destroys self and returns a Particle.
        If entities is given, runs Entity.damage() if it is in the blast radius given by self.explosion_power."""
        self.destroy()

        if self.explosion_power:
            # TODO: compare with edges of rect, not position
            for i in entities:
                if i.distance_to(self.x, self.y) < max(self.explosion_power * 30, 30):
                    i.damage(self.explosion_power)
            return Particle(game=self.game, x=self.x, y=self.y, sprite=Sprite(im.particle.large_explosions, size_multiplier=self.explosion_power), duration=20 * self.explosion_power)
        else:
            return Particle(game=self.game, x=self.x, y=self.y, sprite=Sprite(im.particle.small_explosions), duration=10)

    def update(self) -> None:
        if not 0 <= self.rect.x <= cfg.screen_width:
            self.destroy()

        if self.is_enemy:
            colliding = self.is_colliding(collision.FRIENDLY_AIRCRAFT)
            if colliding:
                # Bullet is colliding with player
                self.game.shake = 8
                for i in colliding:
                    i.damage(10)
                self.explode([self.game.player_controller.entity])
        else:
            self.game.enemy_ai_danger_zones.append(self.y)
            colliding = self.is_colliding(collision.ENEMY_AIRCRAFT)
            if colliding:
                # Bullet colliding with enemy
                for i in colliding:
                    i.damage(10)

                # TODO: this should be handled by another function
                self.explode([enemy for enemy in self.game.entities if isinstance(enemy, Vehicle) and enemy.is_enemy])

        if self.ground_collision():
            self.explode([entity for entity in self.game.entities if isinstance(entity, Vehicle) and entity.is_enemy != self.is_enemy])

        return super().update()

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

class Rocket(Weapon):
    """A Weapon that represents a rocket"""
    def __init__(self, sprite: Sprite|None = None, velocity_x: int = 0, velocity_y: int = 0, drag_multiplier: float = 0.1, is_enemy: bool = False, **kwargs):
        if sprite is None: sprite = Sprite(im.weapons.rocket)
        super().__init__(sprite=sprite, velocity_x=-velocity_x if is_enemy else velocity_x, velocity_y=velocity_y + cfg.physics.bomb_y_velocity_gain, is_enemy=is_enemy, **kwargs)
        self.drag_multiplier = drag_multiplier
        self.drop_delay = 20

    def update(self):
        """Updates this Rocket.
        Speeds up on the X axis when active."""
        super().update()
        if self.drop_delay == 0:
            self.velocity_y -= cfg.physics.rocket_y_stabilisation_multiplier * self.velocity_y * self.drag_multiplier * (1 - abs(self.rotation) / 45)
            self.apply_rotated_velocity(cfg.physics.rocket_thrust * (1 + self.velocity_x / cfg.physics.rocket_terminal_velocity))
        else:
            self.velocity_y += cfg.physics.bomb_y_velocity_gain * (1 + self.velocity_y / cfg.physics.bomb_terminal_velocity)
            self.drop_delay -= 1
