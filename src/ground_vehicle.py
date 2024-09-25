from entity import Entity
from random import randint
from config import cfg
from sprite import Sprite
from images import im
import ai
import pygame
import particle

class GroundVehicle(Entity):
    """Ground vehicle"""
    def __init__(self, sprite: Sprite|None = None, **kwargs):
        if sprite is None: sprite = Sprite(im.ground_vehicles.tank)

        self.speed = randint(1, 50)
        super().__init__(sprite=sprite, x=cfg.screen_width, y=cfg.floor_y - sprite.size[1], **kwargs)
        self.ai = ai.BaseAI(self.sprite.size)
        self.sprite.anim_time *= 50 // self.speed
        self.velocity_x = 0.001 * cfg.screen_width * self.speed - cfg.scroll_speed
        self.is_aircraft = False
        self.is_enemy = True

    def update(self) -> None:
        """Update.
        If the vehicle is outside the screen, delete self"""
        if self.x < 0:
            self.alive = False
        return super().update()

    # TODO: make parent Vehicle class for GV and Aircraft and put this in there
    def display_particle(self, sprite: Sprite, delay: int = 400) -> particle.Particle | None:
        """Returns a Particle with the Sprite if this function has been run longer ago than the delay param.
        The Particle will move with the screen if this Aircraft is not an enemy"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_particle_time > delay:
            self.last_particle_time = current_time
            return particle.Particle(self.x + randint(0, int(self.width)), self.y + randint(0, int(self.height)), sprite=sprite, move_with_screen=not self.is_enemy)
        else: return None
