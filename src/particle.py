from sprite import Sprite
from config import cfg

class Particle:
    """A particle that contains a Sprite with a position."""
    def __init__(self, x: int = 0, y: int = 0, sprite: Sprite = Sprite(), duration: int = 0, scale: float = 1, adjust_pos: bool = True, move_with_screen: bool = False, velocity_x: int = 0, velocity_y: int = 0) -> None:
        """If adjust_pos is True, moves the centre of the particle to x,y"""
        if scale != 1: sprite.set_size(size_multiplier=scale)
        self.sprite = sprite
        self.width, self.height = sprite.size
        self.velocity_x, self.velocity_y = velocity_x, velocity_y
        self.move_with_screen = move_with_screen

        if adjust_pos:
            self.x = x - self.width / 2
            self.y = y - self.height / 2
        else:
            self.x, self.y = x, y

        if duration != 0:
            self.sprite.anim_time = duration * self.sprite.anim_time // self.sprite.anim_frame_count

        self.alive = True

    def draw(self, screen, scroll_speed: int = cfg.scroll_speed):
        """Draws this sprite onto screen.
        If self.move_with_screen is set, move x pos by scroll_speed."""
        if self.move_with_screen: self.x -= scroll_speed

        self.x += self.velocity_x
        self.y += self.velocity_y
        self.alive = self.sprite.draw(screen, self.x, self.y, False)
