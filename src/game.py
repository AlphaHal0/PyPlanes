import pygame
from config import cfg, kb
from random import random, randint, choice
import aircraft
from particle import Particle
from sprite import Sprite
import ground_vehicle
from images import im
from keybind import is_pressed, is_held
from vfx import ScreenDistortion
from display import screen

class Game:
    """A class that represents the game logic"""
    def __init__(self):
        # init vars
        self.enemies = []
        self.enemy_count = cfg.gameplay.initial_enemy_aircraft
        self.scroll_x = [0, 0, 0]
        self.bullets = []
        self.particles = []
        self.enemy_ai_danger_zones = []
        self.score = 0
        self.wave = 1
        self.wave_mode_text_x = cfg.screen_width
        self.wave_mode_text_y = cfg.screen_height // 2 - screen.font.get_height() // 2
        self.running = True
        self.game_paused = False
        self.frame_step = 0
        self.background = [Sprite(i) for i in (im.background.layer_1, im.background.layer_2, im.background.layer_3)]
        self.shake = 0

        if cfg.gameplay.disable_takeoff:
            # Set initial values for when not taking off
            self.wave_warmup_time = 120 if cfg.gameplay.wave_mode else 0
            self.wave_mode_text_opacity = 255
            screen.render_text(f"Wave {self.wave}", display=False, id="wavemode")
            self.scroll_speed = cfg.scroll_speed
            self.pregame_timer = 0
            pygame.mouse.set_visible(cfg.debug.mouse_visibility)
        else:
            # Set initial values for taking off
            self.wave_warmup_time = 0
            self.pregame_timer = 300
            self.scroll_speed = 0
            self.wave_mode_text_opacity = 0

        # init player aircraft
        self.player = aircraft.Aircraft(
            cfg.initial_aircraft_x,
            cfg.initial_aircraft_y if cfg.gameplay.disable_takeoff else cfg.floor_y - im.aircraft.aircraft.get_height(),
            Sprite(im.aircraft.aircraft),
            shoot_cooldown=cfg.gameplay.player_shoot_cooldown,
            bomb_cooldown=cfg.gameplay.player_bomb_cooldown,
            health=cfg.gameplay.initial_health)

        # spawn enemies
        if not cfg.gameplay.wave_mode:
            for i in range(self.enemy_count):
                self.spawn_enemy()

        if cfg.easter_eggs.moth_music_is_main_music:
            pygame.mixer.music.load(f"./res/audio/really_good_soundtrack.mp3", "music_moth")
            pygame.mixer.music.play(-1)

    def spawn_enemy(self, image: pygame.Surface|None = None, difficulty: int = 1, moth: bool = False, type: int = 0):
        if (cfg.easter_eggs.moth_chance and random() <= cfg.easter_eggs.moth_chance) or moth:
            # Spawn moth and play music
            if cfg.easter_eggs.moth_music and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(f"./res/audio/really_good_soundtrack.mp3", "music_moth")
                pygame.mixer.music.play(-1)
            self.enemies.append(aircraft.Moth(cfg.initial_aircraft_y, difficulty))
        else:
            if type == 0: type = randint(1, min(5, difficulty))
            if image is not None: image = Sprite(image)
            self.enemies.append(aircraft.EnemyAircraft(cfg.initial_aircraft_y, image, difficulty, ai_type=type))

    def loop(self):
        """Main game loop"""
        self.draw_background()

        if self.pregame_timer == 0:
            self.logic()
        else:
            self.pregame()

        # Draw aircraft
        self.player.draw()

        self.process_particles()
        self.apply_screen_shake()

        self.hud()

        while self.game_paused and not self.frame_step:
            for event in pygame.event.get((pygame.MOUSEWHEEL, pygame.MOUSEBUTTONDOWN, pygame.QUIT)):
                if event.type == pygame.QUIT: return
                elif is_pressed(event, kb.debug.unpause_game) or is_pressed(event, kb.other.quit):
                    self.game_paused = False
                    print("Game resumed")
                elif is_pressed(event, kb.debug.step_one_frame):
                    self.frame_step = 1
                    break
                elif is_pressed(event, kb.debug.step_5_frames):
                    self.frame_step = 5
                    break
                elif is_pressed(event, kb.debug.step_60_frames):
                    self.frame_step = 60
                    break

        if self.frame_step: self.frame_step -= 1

        # Update display
        screen.update()

    def draw_background(self):
        # Draw background
        i = 2
        for image in self.background:
            image.draw(self.scroll_x[i], 0)
            image.draw(self.scroll_x[i] + cfg.screen_width, 0)
            i -= 1

        # Update scrolling background
        for i in range(3):
            self.scroll_x[i] -= self.scroll_speed // (i+1)

            if self.scroll_x[i] < -cfg.screen_width:
                self.scroll_x[i] = 0

    def process_particles(self):
        self.particles = [particle for particle in self.particles if particle.alive]
        for particle in self.particles:
            particle.draw(self.scroll_speed)

    def apply_screen_shake(self):
        # Apply screen shake
        if self.shake > 0.1:
            shake_mod = int(self.shake * cfg.display.shake_intensity)
            screen.surface.scroll(
                randint(-shake_mod, shake_mod),
                randint(-shake_mod, shake_mod))
            self.shake *= 0.8

    def hud(self):
        """Draw HUD elements"""
        health_bar = pygame.Surface((150,10))
        health_bar.fill(0xFF0000)
        health_bar.fill(0x00FF00, rect=(0,0,(self.player.health/cfg.gameplay.initial_health)*150,10)),

        # Draw health bar
        screen.surface.blit(
            health_bar,
            (self.player.x+(self.player.width//2-80),
            self.player.y-self.player.height)
        )

        scoredisplay = f"Score {self.score} | Difficulty {round(self.enemy_count, 1)}"
        if cfg.gameplay.wave_mode:
            scoredisplay += f"| Wave {self.wave}"
            if self.wave_mode_text_opacity > 0:
                screen.set_cached_text_alpha("wavemode", self.wave_mode_text_opacity)
                screen.display_cached_text("wavemode", self.wave_mode_text_x, self.wave_mode_text_y)
                self.wave_mode_text_x -= cfg.scroll_speed * (self.wave_mode_text_x / cfg.screen_width - 0.4)
                if self.wave_warmup_time <= 0:
                    self.wave_mode_text_opacity -= 2

        if cfg.debug.show_fps: scoredisplay += f" | FPS {round(screen.clock.get_fps())}"
        screen.render_text(scoredisplay, x=0, y=0)

    def logic(self):
        self.process_inputs()
        self.process_player()
        self.process_enemies()
        self.spawn_new_enemies()
        self.update_bullets()

    def process_inputs(self):
        """Process keyboard and mouse inputs"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or is_pressed(event, kb.other.quit):
                self.running = False
            elif is_pressed(event, kb.weapons.shoot):
                new_bullet = self.player.shoot()
                if new_bullet is not None:
                    self.bullets.append(new_bullet)
            elif is_pressed(event, kb.weapons.bomb):
                new_bomb = self.player.bomb()
                if new_bomb is not None:
                    self.bullets.append(new_bomb)
            elif is_pressed(event, kb.weapons.rocket):
                new_rocket = self.player.drop_rocket()
                if new_rocket is not None:
                    self.bullets.append(new_rocket)
            elif is_pressed(event, kb.debug.spawn_enemy):
                while True:
                    event = pygame.event.wait()
                    if event.type == pygame.KEYDOWN:
                        match event.key:
                            case kb.debug.spawn_enemy_ai_1: self.spawn_enemy(difficulty=int(self.enemy_count), type=1)
                            case kb.debug.spawn_enemy_ai_2: self.spawn_enemy(difficulty=int(self.enemy_count), type=2)
                            case kb.debug.spawn_enemy_ai_3: self.spawn_enemy(difficulty=int(self.enemy_count), type=3)
                            case kb.debug.spawn_enemy_ai_4: self.spawn_enemy(difficulty=int(self.enemy_count), type=4)
                            case kb.debug.spawn_enemy_ai_5: self.spawn_enemy(difficulty=int(self.enemy_count), type=5)

                        break

            elif is_pressed(event, kb.debug.spawn_ground_enemy):
                self.enemies.append(ground_vehicle.GroundVehicle())

            elif is_pressed(event, kb.debug.spawn_moth):
                self.spawn_enemy(moth=True, difficulty=int(self.enemy_count))
            elif is_pressed(event, kb.debug.kill_all):
                for enemy in self.enemies:
                    enemy.hit()
            elif is_pressed(event, kb.debug.spawn_particle):
                self.particles.append(Particle(
                    self.player.x,
                    self.player.y,
                    sprite=choice((Sprite(im.particle.large_explosions), Sprite(im.particle.small_explosions), Sprite(im.aircraft.moth))),
                    duration=randint(10, 100),
                    scale=randint(1,5),
                    adjust_pos=False))
            elif is_pressed(event, kb.debug.shockwave):
                self.particles.append(ScreenDistortion(self.player.x+self.player.width//2, self.player.y+-self.player.height//2, 50, direction=self.player.pitch, angle=360, width=10, time_alive=20))

            elif is_pressed(event, kb.debug.pause_game):
                print("Game paused")
                self.game_paused = not self.game_paused

            # pitch
            elif is_pressed(event, kb.movement.pitch_up):
                self.player.set_pitch(20)
            elif is_pressed(event, kb.movement.pitch_down):
                self.player.set_pitch(-20)
            elif is_pressed(event, kb.movement.pitch_down, True) or is_pressed(event, kb.movement.pitch_up, True):
                self.player.set_pitch(0)

        pygame.event.set_grab(True)

        if is_held(kb.weapons.shoot_hold):
            new_bullet = self.player.shoot()
            if new_bullet is not None:
                self.bullets.append(new_bullet)

        if is_held(kb.debug.thrust):
            self.particles.append(Particle(
                self.player.x + self.player.width * 0.3,
                self.player.y + self.player.height * 0.5,
                sprite=Sprite(im.particle.afterburner),
                scale=1,
                velocity_x=-40,
                move_with_screen=True,
                rotation=self.player.pitch,
                adj_velocity_for_rot=True
            ))
            if self.scroll_speed < cfg.scroll_speed * 2:
                self.scroll_speed += 0.2

            self.shake = (self.scroll_speed - cfg.scroll_speed) / cfg.scroll_speed * 5
        else:
            if self.scroll_speed > cfg.scroll_speed:
                self.scroll_speed -= 0.2

    def process_player(self):
        """Update aircraft position and check for collisions"""
        target_x, target_y = pygame.mouse.get_pos()
        self.player.apply_acceleration(target_x, target_y, trackable_distance=50)
        self.player.update()

        if not cfg.debug.invincible: self.player.check_health()

        if self.player.falling:
            particle = self.player.display_particle(Sprite(im.particle.small_explosions, animation_time=5))
            if particle: self.particles.append(particle)
            self.shake = 2

        if self.player.ground_collision():
            self.player.health -= cfg.gameplay.ground_health_decay
            if not cfg.debug.invincible and self.player.health <= 0:
                print("Player hit the floor. Game over.")
                self.running = False
            particle = self.player.display_particle(Sprite(im.particle.small_explosions, animation_time=30, size_multiplier=2), 100)
            if particle:
                self.particles.append(particle)
                self.shake = 8

    def process_enemies(self):
        """Update enemies"""
        self.enemies = [enemy for enemy in self.enemies if enemy.alive]
        for enemy in self.enemies:
            enemy.draw()
            if enemy.is_aircraft:
                enemy.ai_tick(danger_zones=self.enemy_ai_danger_zones, player_y=self.player.y, player_x=self.player.x, enemy_y=enemy.y)
                if enemy.ground_collision():
                    enemy.destroy()
                    self.particles.append(Particle(enemy.x, enemy.y, sprite=Sprite(im.particle.large_explosions, animation_time=40), scale=3, adjust_pos=False, move_with_screen=True))
                    self.score += 20 if cfg.gameplay.wave_mode else 70
                    self.enemy_count += cfg.gameplay.enemy_count_increment
                if enemy.falling:
                    particle = enemy.display_particle(Sprite(im.particle.small_explosions, animation_time=5))
                    if particle: self.particles.append(particle)
            else:
                enemy.update()
            if enemy.ai.shoot:
                self.bullets.append(enemy.shoot())
                enemy.ai.shoot -= 1

            if cfg.debug.show_ai_type:
                ai_marker = pygame.Surface((10,10))
                ai_marker.fill(enemy.ai.debug_color)
                screen.surface.blit(ai_marker, (enemy.x+enemy.sprite.size[0], enemy.y))

    def spawn_new_enemies(self):
        """Try to spawn new enemies"""
        if self.wave_warmup_time:
            self.player.health += self.enemy_count * cfg.gameplay.wave_regen_multiplier
            self.wave_warmup_time -= 1
            if self.wave_warmup_time == 0:
                self.to_spawn = int(self.enemy_count)
                for i in range(self.to_spawn):
                    self.spawn_enemy(difficulty=int(self.enemy_count))

        # Spawn all enemies in one go if cfg.gameplay.wave_mode is True, otherwise spawn one enemy to keep up with the count.
        elif len(self.enemies) < int(self.enemy_count) and not cfg.gameplay.wave_mode:
            self.player.health += self.enemy_count * cfg.gameplay.enemy_regen_multiplier
            self.spawn_enemy(difficulty=int(self.enemy_count))

        elif len(self.enemies) == 0 and cfg.gameplay.wave_mode:
            self.score += 50 * self.to_spawn
            print(f"Wave {self.wave} complete!")
            self.wave += 1
            self.wave_warmup_time = 120
            self.wave_mode_text_x = cfg.screen_width
            self.wave_mode_text_opacity = 255
            screen.render_text(f"Wave {self.wave}", display=False, id="wavemode")

    def update_bullets(self):
        """Update and draw bullets"""

        self.bullets = [bullet for bullet in self.bullets if bullet is not None and bullet.alive]
        self.enemy_ai_danger_zones = []
        for bullet in self.bullets:
            bullet.update()

            if bullet.is_enemy:
                # Bullet is colliding with player
                if bullet.is_colliding(self.player.rect):
                    self.player.health -= 10
                    self.shake = 8
                    self.particles.append(bullet.explode(self.enemies))
            else:
                collided_aircraft = bullet.is_colliding([enemy.rect for enemy in self.enemies])
                if collided_aircraft > -1:
                    if self.enemies[collided_aircraft].hit(): self.score += 30
                    self.particles.append(bullet.explode(self.enemies)) # delete bullet

                # NOT EFFICIENT: I'm sure there's a better way than this
                for i in self.bullets:
                    if bullet.is_colliding_entity(i): # Allow bullets to collide
                        self.particles.append(bullet.explode(self.enemies))
                        i.explode()

                self.enemy_ai_danger_zones.append(bullet.y)

            if bullet.ground_collision():
                self.particles.append(bullet.explode(self.enemies))

            bullet.draw()

    def pregame(self):
        """Runs during takeoff"""

        for event in pygame.event.get():
            if event.type == pygame.QUIT or is_pressed(event, kb.other.quit):
                self.running = False

        if self.pregame_timer > 100:
            self.scroll_speed = int(((300-self.pregame_timer)/200) * cfg.scroll_speed)
        else:
            self.player.apply_acceleration(cfg.initial_aircraft_x, cfg.initial_aircraft_y)
            self.player.update()

        self.pregame_timer -= 1

        if self.pregame_timer == 0:
            self.wave_warmup_time = 120 if cfg.gameplay.wave_mode else 0
            self.wave_mode_text_opacity = 255
            screen.render_text(f"Wave {self.wave}", display=False, id="wavemode")
            self.scroll_speed = cfg.scroll_speed
            pygame.mouse.set_visible(cfg.debug.mouse_visibility)

def play():
    game = Game()

    while game.running:
        game.loop()

    # Quit Pygame
    print(f"Final score: {game.score}")
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    pygame.mixer.stop()
    pygame.mixer.music.stop()
