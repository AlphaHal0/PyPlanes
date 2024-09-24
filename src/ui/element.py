from config import cfg

class UIElement:
    """Base class for all UI elements"""
    def __init__(self, x: int|None = None, y: int|None = None, grid_pos: tuple = (), id: str = ""):
        self.id = id
        self.grid_pos = grid_pos
        if len(grid_pos):
            self.place_on_grid()

        if x is not None: self.x = x
        if y is not None: self.y = y
        self.grid_pos = grid_pos
        self.listen_for_events = False

    def place_on_grid(self):
        """Work out X and Y positions from self.grid_pos"""
        left_margin = cfg.screen_width * cfg.ui.grid_margins[0]
        upper_margin = cfg.screen_height * cfg.ui.grid_margins[1]
        right_margin = cfg.screen_width * cfg.ui.grid_margins[2]
        lower_margin = cfg.screen_height * cfg.ui.grid_margins[3]
        self.x = int((cfg.screen_width - left_margin - right_margin) // cfg.ui.menu_grid_divisions[0] * self.grid_pos[0] + left_margin)
        self.y = int((cfg.screen_height - upper_margin - lower_margin) // cfg.ui.menu_grid_divisions[1] * self.grid_pos[1] + upper_margin)

    def update(self, **kwargs): pass
