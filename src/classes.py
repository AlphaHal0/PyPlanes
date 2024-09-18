import pygame
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

    def update_position(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

    def apply_friction(self):
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction

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
    
    def shoot(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_shot_time > self.shoot_cooldown:
            self.last_shot_time = current_time
            return Bullet(self.x + self.width, self.y + self.height / 2)
        else:
            return None

    def draw(self, screen):
        # pygame.draw.rect(screen, (0, 255, 255), (self.x, self.y, self.width, self.height))
        screen.blit(self.image, (self.x, self.y))

class Entity:
    def __init__(self, rect: pygame.Rect, gravity: int, sprite=None):
        self.rect = rect
        self.gravity = gravity
        self.sprite = sprite
        self.velocity = (0, 0)
    
    def update_position(self):
        self.rect.move_ip(*self.velocity)

    def draw(self, screen):
        if self.sprite is None:
            pygame.draw.rect(screen, (255, 0, 0), self.rect)
        else:
            screen.blit(self.sprite, self.rect)
    
    def is_colliding(self, rect):
        return pygame.Rect.colliderect(self.rect, rect)

class Bullet(Entity):
    def __init__(self, x, y):
        bullet_image = pygame.image.load("./assets/bullets/Shot1.png").convert_alpha()
        bullet_image = pygame.transform.scale(bullet_image, (bullet_image.get_width() * 3, bullet_image.get_height() * 3))
        rect = bullet_image.get_rect(topleft=(x, y))
        super().__init__(rect, 0, bullet_image)
        self.velocity = 15  # Adjust the velocity as needed

    def update_position(self):
        self.rect.move_ip(self.velocity, 0)
    
class Enemy(Entity):
    def __init__(self, rect: pygame.Rect, gravity: int, sprite=None):
        super().__init__(rect, gravity, sprite)