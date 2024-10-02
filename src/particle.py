from sprite import Sprite
from config import cfg
from entity import Entity

class Particle(Entity):
    """A particle that contains a Sprite with a position."""
    def __init__(self, x: int = 0, y: int = 0, duration: int = 0, scale: float = 1, adjust_pos: bool = True, move_with_screen: bool = False, **kwargs) -> None:
        """If adjust_pos is True, moves the centre of the particle to x,y"""
        super().__init__(x=x, y=y, **kwargs)

        if adjust_pos:
            self.x -= self.width / 2
            self.y -= self.height / 2

        if scale != 1: self.sprite.set_size(size_multiplier=scale)
        self.move_with_screen = move_with_screen

        if duration != 0:
            self.sprite.anim_time = duration * self.sprite.anim_time // self.sprite.anim_frame_count

    def draw(self, screen, scroll_speed: int = cfg.scroll_speed):
        """Draws this sprite onto screen.
        If self.move_with_screen is set, move x pos by scroll_speed."""
        if self.move_with_screen: self.x -= scroll_speed

        self.update()
        self.alive = self.sprite.draw(screen, self.x, self.y, False)
