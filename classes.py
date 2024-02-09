import pygame
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Aircraft:
    def __init__(self, width, height, x, y, image):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.image = image
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.8
        self.friction = 0.92
        self.last_shot_time = 0
        self.shoot_cooldown = 400
        self.rect = image.get_rect(topleft=(x, y))
        self.alive = True
        self.falling = False

    def update_position(self):
        if self.falling:
            self.velocity_y = max(2, self.velocity_y) # clamp the velocity so the aircraft is always falling

        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.update((self.x, self.y), (self.width, self.height))

    def apply_friction(self):
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction

    def destroy(self):
        self.alive = False

    def apply_acceleration(self, target_x, target_y, trackable_distance=50):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = max(1, (dx**2 + dy**2)**0.5)

        if distance > trackable_distance:
            normalized_dx = dx / distance
            normalized_dy = dy / distance

            self.velocity_x += normalized_dx * self.acceleration
            self.velocity_y += normalized_dy * self.acceleration

        if self.x < 0:
            self.x = 0
            self.velocity_x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            self.velocity_x = 0

        if self.y < 0:
            self.y = 0
            self.velocity_y = 0
        elif self.y + self.height > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.height
            self.velocity_y = 0

    def ground_collision(self):
        return self.y + self.height > SCREEN_HEIGHT - (0.12 * SCREEN_HEIGHT)
    
    def shoot(self, is_enemy = False):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_shot_time > self.shoot_cooldown:
            self.last_shot_time = current_time
            return Bullet((self.x if is_enemy else self.x + self.width), self.y + self.height / 2, is_enemy)
        else:
            return None

    def draw(self, screen):
        # pygame.draw.rect(screen, (0, 255, 255), (self.x, self.y, self.width, self.height))
        screen.blit(self.image, (self.x, self.y))

# Create a new AI aircraft that inherits properties from Aircraft.
class EnemyAircraft(Aircraft):
    def __init__(self, width, height, y, image):

        # Call Aircraft()
        super().__init__(width, height, SCREEN_WIDTH - width, y, image)

        self.ai = BotAI.Fly(SCREEN_WIDTH - self.x, 0.5 * SCREEN_HEIGHT - (0.12 * SCREEN_HEIGHT))

    def ai_tick(self):
        self.ai.tick()

        self.apply_acceleration(self.ai.target_x, self.ai.target_y, trackable_distance=50)

        self.update_position()
        self.apply_friction()

class BotAI:
    class BaseAI: # The base AI with no special features.
        def __init__(self, target_x, target_y, xmin = SCREEN_WIDTH * 0.5, xmax = SCREEN_WIDTH, ymin = 0, ymax = SCREEN_HEIGHT - (0.2 * SCREEN_HEIGHT), speed = 100):
            self.xmin = xmin
            self.xmax = xmax
            self.ymin = ymin
            self.ymax = ymax
            self.speed = speed
            self.target_x = target_x
            self.target_y = target_y
            self.shoot = 0

        def constrain(self):
            if self.target_x > self.xmax:
                self.target_x -= self.speed
            elif self.target_x < self.xmin:
                self.target_x += random.randint(0, self.speed)

            if self.target_y > self.ymax:
                self.target_y -= self.speed
            elif self.target_y < self.ymin:
                self.target_y += self.speed

        def tick(self):
            self.constrain()

    class Fly(BaseAI): # AI with basic random movements.
        def tick(self):
            self.target_x += random.randint(-self.speed, self.speed)
            self.target_y += random.randint(-self.speed, self.speed)

            if random.random() > 0.9:
                self.shoot += 1 # fire

            self.constrain()

class Entity:
    def __init__(self, rect: pygame.Rect, gravity: int, sprite=None):
        self.rect = rect
        self.gravity = gravity
        self.sprite = sprite
        self.velocity = (0, 0)
        self.alive = True
    
    def update_position(self):
        self.rect.move_ip(*self.velocity)

    def draw(self, screen):
        if self.sprite is None:
            pygame.draw.rect(screen, (255, 0, 0), self.rect)
        else:
            screen.blit(self.sprite, self.rect)

    def destroy(self):
        self.alive = False
    
    def is_colliding(self, rect):
        if isinstance(rect, list):
            return pygame.Rect.collidelist(self.rect, rect)
        else:    
            return pygame.Rect.colliderect(self.rect, rect)

class Bullet(Entity):
    def __init__(self, x, y, is_enemy = False, velocity = 15):
        bullet_image = pygame.image.load("./assets/bullets/Shot1.png").convert_alpha()
        bullet_image = pygame.transform.scale(bullet_image, (bullet_image.get_width() * 3, bullet_image.get_height() * 3))
        if is_enemy:
            bullet_image = pygame.transform.flip(bullet_image, True, False)
        rect = bullet_image.get_rect(topleft=(x, y))
        self.is_enemy = is_enemy

        super().__init__(rect, 0, bullet_image)

        if is_enemy:
            self.velocity = -velocity
        else:
            self.velocity = velocity

    def update_position(self):
        self.rect.move_ip(self.velocity, 0)
    
