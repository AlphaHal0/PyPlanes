#^ ----------------- #
#^ EXPERIMENTAL CODE #
#^ ----------------- #
#^ This code is experimental and may or may not be added
#^ to the final release. It may not be optimised in any way
#^ for code readibility, performance, or compatibility.

from sprite import Sprite
from config import cfg

class MouseEffect:
    def __init__(self, sprite: Sprite, x: int = 0, y: int = 0):
        self.sprite = sprite
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.opacity = 0

    def update(self, mouse_pos):
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        distance = self.distance_to(mouse_pos[0], mouse_pos[1])
        if distance > cfg.ui.mouse_effect_min_distance:
            self.velocity_x += min(dx / distance * 1, cfg.ui.mouse_effect_max_speed)
            self.velocity_y += min(dy / distance * 1, cfg.ui.mouse_effect_max_speed)

        self.velocity_x *= cfg.ui.mouse_effect_drag
        self.velocity_y *= cfg.ui.mouse_effect_drag

        self.x += self.velocity_x
        self.y += self.velocity_y

        self.mouse_effect.draw(self.x-self.sprite.size[0]//2, self.y-self.sprite.size[1]//2)
