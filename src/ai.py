import random
from config import cfg

class BaseAI: # The base AI with no special features.
    def __init__(self, size: tuple):
        self.speed = 100
        self.xmin = cfg.screen_width * 0.5
        self.xmax = cfg.screen_width - size[0] - 10
        self.ymin = 0
        self.ymax = cfg.floor_y - size[1]
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

    def tick(self): pass

class Fly(BaseAI): # AI with basic random movements.
    def tick(self):
        self.target_x += random.randint(-self.speed, self.speed)
        self.target_y += random.randint(-self.speed, self.speed)

        if random.random() > 0.97:
            self.shoot += 1 # fire

        self.constrain()

class Turret(BaseAI): # Move to a random position and shoot.
    def __init__(self, size: tuple):
        self.iteration = 0
        super().__init__(size)

    def tick(self):
        if self.iteration == 0:
            self.target_x = random.randint(int(self.xmin), int(self.xmax))
            self.target_y = random.randint(int(self.ymin), int(self.ymax))
            self.iteration = 100
        else:
            if self.iteration <= 50 and self.iteration % 10 == 0:
                self.shoot += 1
            self.iteration -= 1
        self.constrain()
