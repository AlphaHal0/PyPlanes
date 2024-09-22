import pygame
import random
import particle
from config import cfg
import ai
import weapon
from entity import Entity
from sprite import Sprite
import images

class Aircraft(Entity):
    def __init__(self, x: int, y: int, sprite: Sprite = Sprite(), is_enemy: bool = False, shoot_cooldown: int = cfg.shoot_cooldown, spawn_cooldown: int = cfg.spawn_cooldown, health: int = 100, bomb_cooldown: int = cfg.bomb_cooldown):
        self.acceleration = 0.8
        self.friction = 0.92
        self.shoot_cooldown = 0
        self.bomb_cooldown = 0
        self.max_shoot_cooldown = shoot_cooldown
        self.spawn_cooldown = spawn_cooldown
        self.time_of_spawn = pygame.time.get_ticks()
        self.alive = True
        self.falling = False
        self.is_enemy = is_enemy
        self.last_particle_time = 0
        self.health = health
        self.max_bomb_cooldown = bomb_cooldown
        self.pitch = 0
        self.target_pitch = 0
        super().__init__(sprite, x, y)

    def update_position(self) -> None:
        if self.shoot_cooldown: self.shoot_cooldown -= 1
        if self.bomb_cooldown: self.bomb_cooldown -= 1

        if self.target_pitch != self.pitch:
            self.sprite.rotate(self.pitch)
            if self.pitch > self.target_pitch:
                self.pitch -= 1
            else:
                self.pitch += 1

        if self.falling:
            self.velocity_y = max(2, self.velocity_y) # clamp the velocity so the aircraft is always falling

        super().update_position()

    def set_pitch(self, value: int = 0) -> int:
        self.target_pitch = value
        return self.pitch

    def apply_friction(self) -> None:
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction

    def destroy(self) -> None:
        self.alive = False

    def fall(self) -> bool:
        if pygame.time.get_ticks() - self.time_of_spawn < self.spawn_cooldown: return False
        if not self.falling:
            self.falling = True
            self.sprite.rotate(10 if self.is_enemy else -10)
        else: return False

    def display_particle(self, sprite: Sprite) -> particle.Particle | None:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_particle_time > 400:
            self.last_particle_time = current_time
            return particle.Particle(self.x + random.randint(0, int(self.width)), self.y + random.randint(0, int(self.height)), sprite=sprite, duration=10)
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
        elif self.x + self.width > cfg.screen_width:
            self.x = cfg.screen_width - self.width
            self.velocity_x = 0

        if self.y < 0:
            self.y = 0
            self.velocity_y = 0
        elif self.y + self.height > cfg.floor_y:
            self.y = cfg.floor_y - self.height
            self.velocity_y = 0
    
    def shoot(self) -> weapon.Bullet | None:
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.max_shoot_cooldown
            return weapon.Bullet(
                (self.x if self.is_enemy else self.x + self.width),
                self.y + self.height / 2,
                self.is_enemy,
                velocity_x=cfg.bullet_velocity+(self.velocity_x*cfg.weapon_relative_velocity_multiplier),
                rotation=self.pitch)
        else:
            return None
    
    def bomb(self) -> weapon.Bomb | None:
        if self.bomb_cooldown <= 0:
            self.bomb_cooldown = self.max_bomb_cooldown
            return weapon.Bomb(
                (self.x + self.width // 2),
                self.y + self.height,
                self.is_enemy,
                self.velocity_x,
                explosion_power=random.randint(4,6),
                rotation=self.pitch
            )
        else:
            return None

# Create a new AI aircraft that inherits properties from Aircraft.
class EnemyAircraft(Aircraft):
    def __init__(self, y: int, sprite: Sprite, difficulty: int = 1, ai_type: int = 1):
        # Call Aircraft()
        super().__init__(cfg.screen_width, y, sprite, True, 50)

        size = self.sprite.size
        if ai_type == 1: self.ai = ai.Fly(size, difficulty, self.max_shoot_cooldown)
        elif ai_type == 2: self.ai = ai.Turret(size, difficulty, self.max_shoot_cooldown)
        elif ai_type == 3: self.ai = ai.Dodger(size, difficulty, self.max_shoot_cooldown)
        elif ai_type == 4: self.ai = ai.Offence(size, difficulty, self.max_shoot_cooldown)
        else: self.ai = ai.BaseAI(size)

    def ai_tick(self, **ctx):
        self.ai.tick(ctx)

        self.apply_acceleration(self.ai.target_x, self.ai.target_y, trackable_distance=50)

        self.update_position()
        self.apply_friction()

    def draw(self, screen: pygame.Surface) -> None:
        if cfg.show_target_traces:
            pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (self.ai.target_x, self.ai.target_y), 5)
        return super().draw(screen)

class Moth(EnemyAircraft):
    def __init__(self, y: int, difficulty: int = 1):
        super().__init__(y, Sprite(images.moth_images, animation_time=random.randint(1, 10)), difficulty)

    def destroy(self) -> None:
        if not cfg.moth_music_is_main_music:
            pygame.mixer.music.fadeout(1000)
        super().destroy()
