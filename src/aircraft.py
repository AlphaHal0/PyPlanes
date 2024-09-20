import pygame
import random
import particle
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, BULLET_VELOCITY, WEAPON_RELATIVE_VELOCITY_MULTIPLIER, SHOOT_COOLDOWN, BOMB_COOLDOWN, SPAWN_COOLDOWN
import ai
import weapon
from entity import Entity

class Aircraft(Entity):
    def __init__(self, width: int, height: int, x: int, y: int, image: pygame.Surface, is_enemy: bool = False, shoot_cooldown: int = SHOOT_COOLDOWN, spawn_cooldown: int = SPAWN_COOLDOWN, health: int = 100, bomb_cooldown: int = BOMB_COOLDOWN, velocity_x: int = 0, velocity_y : int = 0):
        self.width = width
        self.height = height
        self.acceleration = 0.8
        self.friction = 0.92
        self.last_shot_time = 0
        self.last_bomb_time = 0
        self.shoot_cooldown = shoot_cooldown
        self.spawn_cooldown = spawn_cooldown
        self.time_of_spawn = pygame.time.get_ticks()
        self.alive = True
        self.falling = False
        self.is_enemy = is_enemy
        self.last_particle_time = 0
        self.health = health
        self.bomb_cooldown = bomb_cooldown
        super().__init__(image.get_rect(topleft=(x, y)), 0, image, x, y, velocity_x, velocity_y)

    def update_position(self) -> None:
        if self.falling:
            self.velocity_y = max(2, self.velocity_y) # clamp the velocity so the aircraft is always falling

        super().update_position()

    def apply_friction(self) -> None:
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction

    def destroy(self) -> None:
        self.alive = False

    def fall(self) -> bool:
        if pygame.time.get_ticks() - self.time_of_spawn < self.spawn_cooldown: return False
        if not self.falling:
            self.falling = True
            self.sprite = pygame.transform.rotate(self.sprite, 10 if self.is_enemy else -10)
            return True
        else: return False

    def display_particle(self, image: pygame.Surface|None = None, images: list[pygame.Surface]|None = None) -> particle.Particle | None:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_particle_time > 400:
            self.last_particle_time = current_time
            return particle.Particle(self.x + random.randint(0, int(self.width)), self.y + random.randint(0, int(self.height)), image=image, images=images, duration=100)
        else: return None

    def check_health(self) -> bool:
        if self.health == 0:
            return self.fall()
            
    def apply_acceleration(self, target_x: int, target_y: int, trackable_distance: int = 50) -> None:
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
    
    def shoot(self) -> weapon.Bullet | None:
        current_time = pygame.time.get_ticks()

        if current_time - self.last_shot_time > self.shoot_cooldown:
            self.last_shot_time = current_time
            return weapon.Bullet(
                (self.x if self.is_enemy else self.x + self.width),
                self.y + self.height / 2,
                self.is_enemy,
                velocity_x=BULLET_VELOCITY+(self.velocity_x*WEAPON_RELATIVE_VELOCITY_MULTIPLIER))
        else:
            return None
    
    def bomb(self) -> weapon.Bomb | None:
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_bomb_time > self.bomb_cooldown:
            self.last_bomb_time = current_time
            return weapon.Bomb(
                (self.x + self.width // 2),
                self.y + self.height,
                self.is_enemy,
                self.velocity_x,
                explosion_power=random.randint(1,10)
            )
        else:
            return None

# Create a new AI aircraft that inherits properties from Aircraft.
class EnemyAircraft(Aircraft):
    def __init__(self, width: int, height: int, y: int, image: pygame.Surface):
        # Call Aircraft()
        super().__init__(width, height, SCREEN_WIDTH, y, image, True, 50)

        ai_type = random.randint(1, 2)

        if ai_type == 1: self.ai = ai.Fly()
        elif ai_type == 2: self.ai = ai.Turret()
        else: self.ai = ai.BaseAI()

    def ai_tick(self):
        self.ai.tick()

        self.apply_acceleration(self.ai.target_x, self.ai.target_y, trackable_distance=50)

        self.update_position()
        self.apply_friction()
