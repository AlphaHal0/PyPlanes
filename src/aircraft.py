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
    """An Entity with aircraft mechanics"""
    def __init__(self, x: int, y: int, sprite: Sprite = Sprite(), is_enemy: bool = False, shoot_cooldown: int = cfg.gameplay.enemy_shoot_cooldown, spawn_cooldown: int = cfg.gameplay.spawn_cooldown, health: int = 100, bomb_cooldown: int = cfg.gameplay.enemy_bomb_cooldown):
        self.acceleration = cfg.physics.aircraft_acceleration
        self.terminal_velocity = cfg.physics.aircraft_terminal_velocity
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

    def update(self) -> None:
        """Tick"""
        if self.shoot_cooldown: self.shoot_cooldown -= 1
        if self.bomb_cooldown: self.bomb_cooldown -= 1

        if self.falling:
            self.velocity_y = max(2, self.velocity_y) # clamp the velocity so the aircraft is always falling

        elif self.target_pitch != self.pitch:
            self.sprite.rotate(self.pitch)
            if self.pitch > self.target_pitch:
                self.pitch -= 1
            else:
                self.pitch += 1

        super().update()

    def set_pitch(self, value: int = 0) -> int:
        """Sets pitch. Will not work if aircraft is falling."""
        if not self.falling:
            self.target_pitch = value
        return self.pitch

    def fall(self) -> bool:
        """Marks the aircraft as 'falling' - its movement and rotation is limited to downwards.
        Returns False if already falling, else True"""
        if pygame.time.get_ticks() - self.time_of_spawn < self.spawn_cooldown: return False
        if not self.falling:
            self.falling = True
            self.pitch = 10 if self.is_enemy else -10
            self.sprite.rotate(self.pitch)
            self.max_shoot_cooldown *= cfg.gameplay.crashing_shoot_multiplier
        else: return False

    def display_particle(self, sprite: Sprite, delay: int = 400) -> particle.Particle | None:
        """Returns a Particle with the Sprite if this function has been run longer ago than the delay param.
        The Particle will move with the screen if this Aircraft is not an enemy"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_particle_time > delay:
            self.last_particle_time = current_time
            return particle.Particle(self.x + random.randint(0, int(self.width)), self.y + random.randint(0, int(self.height)), sprite=sprite, move_with_screen=not self.is_enemy)
        else: return None

    def check_health(self) -> bool:
        """Check if the Aircraft's health is less than or equal to 0.
        If so, runs and returns the result from self.fall()"""
        if self.health <= 0:
            return self.fall()
            
    def apply_acceleration(self, target_x: int, target_y: int, trackable_distance: int = 50) -> None:
        """Accelerates towards the target pos if the distance is greater than trackable_distance"""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = self.distance_to(target_x, target_y)

        if self.x < 0:
            self.x = 0
            self.velocity_x = 0
        elif self.x + self.width > cfg.screen_width:
            self.x = cfg.screen_width - self.width
            self.velocity_x = 0
        elif distance > trackable_distance:
            self.velocity_x += min(dx / distance * self.acceleration, self.terminal_velocity)


        if self.y < 0:
            self.y = 0
            self.velocity_y = 0
        elif self.y + self.height > cfg.floor_y:
            self.y = cfg.floor_y - self.height
            self.velocity_y = 0
        elif distance > trackable_distance:
            self.velocity_y += min(dy / distance * self.acceleration, self.terminal_velocity)

        self.velocity_x *= cfg.physics.aircraft_drag
        self.velocity_y *= cfg.physics.aircraft_drag
    
    def shoot(self, id: str = 0) -> weapon.Bullet | None:
        """Returns a shot weapon.Bullet if not on cooldown, otherwise None"""
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.max_shoot_cooldown
            return weapon.Bullet(
                x=(self.x if self.is_enemy else self.x + self.width),
                y=self.y + self.height / 2,
                is_enemy=self.is_enemy,
                velocity_x=cfg.physics.bullet_velocity+(self.velocity_x*cfg.physics.weapon_velocity_multiplier),
                rotation=self.pitch,
                id=id)
        else:
            return None
    
    def bomb(self) -> weapon.Bomb | None:
        """Returns a shot weapon.Bomb if not on cooldown, otherwise None"""
        if self.bomb_cooldown <= 0:
            self.bomb_cooldown = self.max_bomb_cooldown
            return weapon.Bomb(
                x=(self.x + self.width // 2),
                y=self.y + self.height,
                is_enemy=self.is_enemy,
                velocity_x=self.velocity_x,
                explosion_power=random.randint(4,6),
                rotation=self.pitch
            )
        else:
            return None

# Create a new AI aircraft that inherits properties from Aircraft.
class EnemyAircraft(Aircraft):
    def __init__(self, y: int, sprite: Sprite, difficulty: int = 1, ai_type: int = 1):
        """An Aircraft with enemy AI"""
        super().__init__(x=cfg.screen_width, y=y, sprite=sprite, is_enemy=True, shoot_cooldown=50)

        size = self.sprite.size
        if ai_type == 1: self.ai = ai.Fly(size, difficulty, self.max_shoot_cooldown)
        elif ai_type == 2: self.ai = ai.Turret(size, difficulty, self.max_shoot_cooldown)
        elif ai_type == 3: self.ai = ai.Dodger(size, difficulty, self.max_shoot_cooldown)
        elif ai_type == 4: self.ai = ai.Offence(size, difficulty, self.max_shoot_cooldown)
        else: self.ai = ai.BaseAI(size)

    def ai_tick(self, **ctx):
        """Ticks the EnemyAircraft's AI and runs self.update()"""
        self.ai.tick(ctx)
        self.apply_acceleration(self.ai.target_x, self.ai.target_y, trackable_distance=50)
        self.update()

    def draw(self, screen: pygame.Surface) -> None:
        if cfg.debug.show_target_traces:
            pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (self.ai.target_x, self.ai.target_y), 5)
        return super().draw(screen)

class Moth(EnemyAircraft):
    def __init__(self, y: int, difficulty: int = 1):
        """An EnemyAircraft that is a moth."""
        super().__init__(y, Sprite(images.moth_images, animation_time=random.randint(1, 10)), difficulty)

    def destroy(self) -> None:
        if not cfg.easter_eggs.moth_music_is_main_music:
            pygame.mixer.music.fadeout(1000)
        super().destroy()
