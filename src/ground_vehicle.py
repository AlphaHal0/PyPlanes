from vehicle import Vehicle
from random import randint
from config import cfg
from sprite import Sprite
from images import im
import ai
import pygame

class GroundVehicle(Vehicle):
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
        self.inert = False # becomes inert when hit

    def update(self) -> None:
        """Update.
        If the vehicle is outside the screen, delete self"""
        if self.x < 0:
            self.alive = False
        return super().update()

    def hit(self) -> bool:
        if pygame.time.get_ticks() - self.time_of_spawn < self.spawn_cooldown: return False
        if not self.inert:
            self.inert = True
            self.sprite.anim_time = 60
            return True
        else:
            return False
