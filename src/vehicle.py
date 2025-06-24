import pygame
import random
from entity import Entity
from sprite import Sprite
from config import cfg
import vfx
import particle
from display import screen

class bar_condition:
    """Constants for health bar draw conditions"""
    HIDDEN = 0 # bar never draws
    ALWAYS = 1 # always draw
    WHEN_BELOW_MAX = 2 # only draw when health < max_health
    WHEN_BELOW_MAX_AND_NOT_INERT = 3

class Vehicle(Entity):
    def __init__(self, is_enemy: bool = False, max_health: float = 0.0, bar_condition: int = bar_condition.HIDDEN, **kwargs):
        self.is_enemy = is_enemy
        self.max_health = max_health
        self.health = max_health
        self.inert = False
        self.bar_condition = bar_condition # condition for drawing health bar
        super().__init__(**kwargs)

    def draw(self):
        super().draw()
        if self.bar_condition == 1 or ((self.bar_condition >= 2 and self.health < self.max_health) and (self.bar_condition == 2 or (self.bar_condition == 3 and not self.inert))):
            health_bar = pygame.Surface((150,10))
            health_bar.fill(0xFF0000)
            health_bar.fill(0x00FF00, rect=(0,0,(self.health/self.max_health)*150,10)),

            # Draw health bar
            screen.surface.blit(
                health_bar,
                (self.x+(self.width//2-80),
                self.y-self.height)
            )

    def die(self):
        if pygame.time.get_ticks() - self.time_of_spawn < self.spawn_cooldown: return False
        if not self.inert:
            self.inert = True

    def damage(self, amt: float):
        self.health -= amt
        self.check_health()

    def check_health(self) -> bool:
        """Check if the Vehicle's health is less than or equal to 0.
        If so, runs and returns the result from self.die()"""
        if self.health > self.max_health:
            self.health = self.max_health
        if self.health <= 0:
            return self.die()

    def spawn_particle(self, sprite: Sprite, delay: int = 400, **kwargs):
        """Returns a Particle with the Sprite if this function has been run longer ago than the delay param.
        The Particle will move with the screen if this Aircraft is not an enemy"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_particle_time > delay:
            self.last_particle_time = current_time

            if cfg.easter_eggs.secret_option: # Don't mind this :)
                return vfx.ScreenDistortion(game=self.game, x=self.x + random.randint(0, int(self.width)), y=self.y + random.randint(0, int(self.height)), direction=50, angle=360, width=sprite.size[0] // 5, time_alive=20, move_with_screen=not self.is_enemy, **kwargs)
            else:
                return particle.Particle(game=self.game, x=self.x + random.randint(0, int(self.width)), y=self.y + random.randint(0, int(self.height)), sprite=sprite, **kwargs)
