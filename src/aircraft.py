import pygame
import random
from config import cfg
import ai
import weapon
from vehicle import Vehicle, bar_condition
from sprite import Sprite
import collision
from images import im
from display import screen
import physics

class Aircraft(Vehicle):
    """An Entity with aircraft mechanics"""
    def __init__(self, is_enemy: bool = False, shoot_cooldown: int = cfg.gameplay.enemy_shoot_cooldown, bomb_cooldown: int = cfg.gameplay.enemy_bomb_cooldown, **kwargs):
        self.acceleration = cfg.physics.aircraft_acceleration
        self.terminal_velocity = cfg.physics.aircraft_terminal_velocity
        self.shoot_cooldown = 0
        self.bomb_cooldown = 0
        self.max_shoot_cooldown = shoot_cooldown
        self.falling = False
        self.last_particle_time = 0
        self.max_bomb_cooldown = bomb_cooldown
        self.pitch = 0
        self.target_pitch = 0
        # Enable advanced physics if aircraft belongs to player and advanced physics is enabled
        self.enable_advanced_physics = (not is_enemy) and cfg.advanced_phys.enable_advanced_physics
        if self.enable_advanced_physics: self.physics = physics.AircraftPhysics()

        super().__init__(is_enemy=is_enemy, **kwargs)

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

        if self.ground_collision():
            if self.health <= 0:
                self.spawn_particle(sprite=Sprite(im.particle.large_explosions, animation_time=40), scale=3, adjust_pos=False, move_with_screen=True)
                self.game.player_controller.score += 20 if cfg.gameplay.wave_mode else 70
                self.game.enemy_count += cfg.gameplay.enemy_count_increment
                self.destroy()
            else:
                self.damage(cfg.gameplay.ground_health_decay)
                self.spawn_particle(sprite=Sprite(im.particle.small_explosions, animation_time=30, size_multiplier=2), delay=100, move_with_screen=True)
        if self.falling:
            self.spawn_particle(Sprite(im.particle.small_explosions, animation_time=5))

        super().update()

    def set_pitch(self, value: int = 0) -> int:
        """Sets pitch. Will not work if aircraft is falling."""
        if not self.falling:
            self.target_pitch = value
        return self.pitch

    def die(self) -> bool:
        """Marks the aircraft as 'falling' - its movement and rotation is limited to downwards.
        Returns False if already falling, else True"""
        if pygame.time.get_ticks() - self.time_of_spawn < self.spawn_cooldown: return False
        if not self.falling:
            self.falling = True
            self.inert = True
            self.pitch = 10 if self.is_enemy else -10
            self.sprite.rotate(self.pitch)
            self.max_shoot_cooldown *= cfg.gameplay.crashing_shoot_multiplier
        else: return False

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

    def shoot(self):
        """Summons a weapon.Bullet if not on cooldown, otherwise None"""
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.max_shoot_cooldown
            weapon.Bullet(
                game=self.game,
                x=(self.x if self.is_enemy else self.x + self.width),
                y=self.y + self.height / 2,
                is_enemy=self.is_enemy,
                velocity_x=(cfg.physics.enemy_bullet_velocity if self.is_enemy else cfg.physics.player_bullet_velocity) + (self.velocity_x*cfg.physics.weapon_velocity_multiplier),
                rotation=self.pitch,
                collision_mask=collision.ENEMY_WEAPON if self.is_enemy else collision.FRIENDLY_WEAPON)

    def bomb(self):
        """Summons a weapon.Bomb if not on cooldown, otherwise None"""
        if self.bomb_cooldown <= 0:
            self.bomb_cooldown = self.max_bomb_cooldown
            weapon.Bomb(
                game=self.game,
                x=(self.x + self.width // 2),
                y=self.y + self.height,
                is_enemy=self.is_enemy,
                velocity_x=self.velocity_x,
                velocity_y=self.velocity_y * cfg.physics.bomb_init_y_multiplier,
                explosion_power=random.randint(4,6),
                rotation=self.pitch,
                collision_mask=collision.ENEMY_WEAPON if self.is_enemy else collision.FRIENDLY_WEAPON)

    def rocket(self):
        """Summons a weapon.Rocket if not on cooldown, otherwise None"""
        if self.bomb_cooldown <= 0:
            self.bomb_cooldown = self.max_bomb_cooldown
            weapon.Rocket(
                game=self.game,
                x=(self.x + self.width // 2),
                y=self.y + self.height,
                is_enemy=self.is_enemy,
                velocity_x=self.velocity_x,
                velocity_y=self.velocity_y * cfg.physics.bomb_init_y_multiplier,
                explosion_power=random.randint(4,6),
                rotation=self.pitch,
                collision_mask=collision.ENEMY_WEAPON if self.is_enemy else collision.FRIENDLY_WEAPON)

class EnemyAircraft(Aircraft):
    """An Aircraft with enemy AI"""
    def __init__(self, sprite: Sprite|None = None, difficulty: int = 1, ai_type: int = 1, max_health: float = -1.0, **kwargs):

        if sprite is None: sprite = Sprite(ai.ai_types[ai_type].default_aircraft_img)
        size = sprite.size
        # Get type from index and init AI class
        self.ai: ai.BaseAI = ai.ai_types[ai_type](size=size, difficulty=difficulty, fire_rate=cfg.gameplay.enemy_shoot_cooldown)

        if max_health == -1.0:
            # if max_health argument left blank, generate a random health amount
            max_health=random.randint(0, difficulty)

        super().__init__(x=cfg.screen_width, sprite=sprite, is_enemy=True, max_health=random.randint(0, difficulty), shoot_cooldown=cfg.gameplay.enemy_shoot_cooldown, bar_condition=bar_condition.WHEN_BELOW_MAX_AND_NOT_INERT, collision_mask=collision.ENEMY_AIRCRAFT, **kwargs)

    def update(self):
        self.ai.tick(danger_zones=self.game.enemy_ai_danger_zones, player_y=self.game.player_controller.entity.y, player_x=self.game.player_controller.entity.x, enemy_y=self.y)
        self.apply_acceleration(self.ai.target_x, self.ai.target_y, trackable_distance=50)
        if self.ai.shoot:
                self.shoot()
                self.ai.shoot -= 1

        if cfg.debug.show_ai_type:
            ai_marker = pygame.Surface((10,10))
            ai_marker.fill(self.ai.debug_color)
            screen.surface.blit(ai_marker, (self.x+self.sprite.size[0], self.y))

        return super().update()

    def draw(self):
        super().draw()
        if cfg.debug.show_target_traces:
            pygame.draw.line(screen.surface, (255, 0, 0), (self.x, self.y), (self.ai.target_x, self.ai.target_y), 5)

class Moth(EnemyAircraft):
    """An EnemyAircraft that is a moth"""
    def __init__(self, **kwargs):
        super().__init__(sprite=Sprite(im.aircraft.moth, animation_time=random.randint(1, 10)), max_health=200, **kwargs)

    def destroy(self) -> None:
        if not cfg.easter_eggs.moth_music_is_main_music:
            pygame.mixer.music.fadeout(1000)
        super().destroy()
