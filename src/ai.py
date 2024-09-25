import random
from config import cfg

class BaseAI: 
    """The base AI with no special features."""
    debug_color = 0x000000
    def __init__(self, size: tuple, difficulty: int, fire_rate: int):
        self.speed = 100
        self.fire_rate = fire_rate
        self.difficulty = difficulty
        self.xmin = cfg.screen_width * 0.5
        self.xmax = cfg.screen_width - size[0] - 10
        self.ymin = 0
        self.ymax = cfg.floor_y - size[1] - 50
        self.target_x = self.xmax
        self.target_y = self.ymax * random.random() + self.ymin
        self.shoot = 0

    def constrain(self):
        if self.target_x > self.xmax:
            self.target_x = self.xmax + 10
        elif self.target_x < self.xmin:
            self.target_x += random.randint(0, self.speed)

        if self.target_y > self.ymax:
            self.target_y = self.ymax + 10
        elif self.target_y < self.ymin:
            self.target_y = self.ymin + 10

    def tick(self, ctx: dict): 
        self.constrain()

class Fly(BaseAI): 
    """AI with basic random movements."""
    debug_color = 0xFF0000
    def tick(self, ctx: dict): # What is ctx? Why is it not used? Why is it still defined? UwU
        self.target_x += random.randint(-self.speed, self.speed)
        self.target_y += random.randint(-self.speed, self.speed)

        if random.random() > 0.97:
            self.shoot += 1 # fire

class Turret(BaseAI): 
    """Move to a random position and shoot."""
    debug_color = 0x00FF00
    def __init__(self, size: tuple, difficulty: int, fire_rate: int):
        super().__init__(size, difficulty, fire_rate)
        self.iteration = 0
        self.max_iteration = 100 + self.difficulty * self.fire_rate

    def tick(self, ctx: dict):
        if self.iteration == 0:
            self.target_x = random.randint(int(self.xmin), int(self.xmax))
            self.target_y = random.randint(int(self.ymin), int(self.ymax))
            self.iteration = self.max_iteration
        else:
            if self.iteration <= self.max_iteration - 100 and self.iteration % (self.fire_rate + 1) == 1:
                self.shoot += 1 # fire
            self.iteration -= 1

class Dodger(BaseAI): 
    """Avoid player bullets."""
    debug_color = 0xFFFF00
    def __init__(self, size: tuple, difficulty: int, fire_rate: int):
        super().__init__(size, difficulty, fire_rate)
        self.max_shoot_time = fire_rate * max(1, 5 - difficulty//5)
        self.shoot_time = self.max_shoot_time

    def tick(self, ctx: dict):
        c = 0
        while self.check_is_obstructed(ctx["danger_zones"]) and c < 10: # limit to 10 attempts because UwU
            self.target_y = random.randint(int(self.ymin), int(self.ymax))
            self.target_x = random.randint(int(self.xmin), int(self.xmax))
            c += 1

        if self.shoot_time == 0:
            self.shoot += 1
            self.shoot_time = self.max_shoot_time
        else:
            self.shoot_time -= 1
        
    def check_is_obstructed(self, danger_zones: list):
        for i in danger_zones:
            if abs(self.target_y-i) < 100:
                return True
        return False
    
class Offence(BaseAI): 
    """Follow the player."""
    debug_color = 0x0000FF
    def __init__(self, size: tuple, difficulty: int, fire_rate: int):
        super().__init__(size, difficulty, fire_rate)
        self.max_shoot_time = cfg.gameplay.enemy_shoot_cooldown * max(1, 5 - difficulty//5)
        self.shoot_time = self.max_shoot_time
        self.target_x = random.randint(int(self.xmin), int(self.xmax))

    def tick(self, ctx: dict):
        self.target_y = ctx['player_y']

        if self.shoot_time == 0:
            self.shoot += 1
            self.shoot_time = self.max_shoot_time
        else:
            self.shoot_time -= 1

class Bomber(BaseAI):
    """Shoot player from in front angles
    
        1. Must fly at top 10% of screen
        2. Must shoot at player if they are 0 to -80 degrees in front and below them or up to 10 degrees above
        3. Must not rotate to shoot player
    """
    debug_color = 0x00FFFF
    def __init__(self, size: tuple, difficulty: int, fire_rate: int):
        super().__init__(size, difficulty, fire_rate)
        self.ymin = cfg.screen_height * cfg.aircraft.bomber_minimum_y

        
    def tick(self, ctx: dict):
        
        self.target_x = random.randint(int(self.xmin), int(self.xmax))
        self.target_y = random.randint(int(self.ymin), int(self.ymax))
        

        self.shoot += 1