import pygame
from config import cfg, kb
from random import random, randint
import aircraft
from sprite import Sprite
from images import im
from keybind import is_pressed
from player import PlayerController
from vehicle import bar_condition, Vehicle
from display import screen
import collision

# ----------------------------- #
# TODO: Change collision system #
# ----------------------------- #

#* Takeoff animation is currently hard-disabled

class Game:
    """A class that represents the game logic"""
    def __init__(self):
        # init vars
        self.entities = []
        self.enemy_count = cfg.gameplay.initial_enemy_aircraft # Number of entities that should be on screen, or that spawn at the start of a wave
        self.scroll_x = [0, 0, 0] # Background scroll of each parallax layer
        self.enemy_ai_danger_zones = [] # Areas of the screen that the AI should avoid (not hard limits)
        self.wave = 1
        self.wave_mode_text_x = cfg.screen_width
        self.wave_mode_text_y = cfg.screen_height // 2 - screen.font.get_height() // 2
        self.running = True
        self.game_paused = False
        self.frame_step = 0 # number of frames to step if the game is paused
        self.background = [Sprite(i, disable_debug_size_box=True) for i in (im.background.layer_1, im.background.layer_2, im.background.layer_3)] # background sprites
        self.shake = 0 # screen shake

    def begin(self):
        """Start the game"""
        if cfg.gameplay.disable_takeoff:
            self.finish_takeoff()
        else:
            # Set values for taking off animation
            self.wave_warmup_time = 0
            self.pregame_timer = 300
            self.scroll_speed = 0
            self.wave_mode_text_opacity = 0

        # init player aircraft
        # self.player holds the index of the controlled entity
        self.player = aircraft.Aircraft(
            game=self,
            is_enemy=False,
            x=cfg.initial_aircraft_x,
            y=cfg.initial_aircraft_y if cfg.gameplay.disable_takeoff else cfg.floor_y - im.aircraft.aircraft.get_height(),
            sprite=Sprite(im.aircraft.aircraft),
            shoot_cooldown=cfg.gameplay.player_shoot_cooldown,
            bomb_cooldown=cfg.gameplay.player_bomb_cooldown,
            max_health=cfg.gameplay.initial_health,
            bar_condition=bar_condition.ALWAYS,
            collision_mask=collision.FRIENDLY_AIRCRAFT
        ).index

        # Class to handle player inputs and control an associated player Entity
        self.player_controller = PlayerController(game=self, entity=self.entities[self.player])

        # spawn enemies
        if not cfg.gameplay.wave_mode:
            for i in range(self.enemy_count):
                self.spawn_enemy()

        # Play music if enabled
        if cfg.easter_eggs.moth_music_is_main_music:
            pygame.mixer.music.load(f"./res/audio/moth.ogg", "music_moth")
            pygame.mixer.music.play(-1)

    def loop(self):
        """Main game loop"""
        if not cfg.easter_eggs.secret_option: # Secret option prevents background from being drawn
            self.draw_background()

        if self.pregame_timer > 0: # Takeoff animation timer
            self.pregame()
            return

        self.player_controller.update()
        self.update_entities()
        self.spawn_new_enemies()
        self.apply_screen_shake()
        self.hud()

        # Logic when game is paused
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
        # Draw background - bottom layer first
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

    def pregame(self):
        """Runs during takeoff animation"""

        for event in pygame.event.get():
            if event.type == pygame.QUIT or is_pressed(event, kb.other.quit):
                self.running = False

        if self.pregame_timer > 100:
            # Ramp up the background speed
            self.scroll_speed = int(((300-self.pregame_timer)/200) * cfg.scroll_speed)
            self.player_controller.entity.draw()
        else:
            # Tell the aircraft to go to starting position in the air
            self.player_controller.entity.apply_acceleration(cfg.initial_aircraft_x, cfg.initial_aircraft_y)
            self.player_controller.entity.update()

        self.pregame_timer -= 1

        if self.pregame_timer == 0:
            self.finish_takeoff() # Start the game


        screen.update()

    def finish_takeoff(self):
        """Runs after the takeoff animation has finished"""
        self.wave_warmup_time = 120 if cfg.gameplay.wave_mode else 0 # time between waves
        self.wave_mode_text_opacity = 255
        screen.render_text(f"Wave {self.wave}", display=False, id="wavemode")
        self.scroll_speed = cfg.scroll_speed
        pygame.mouse.set_visible(cfg.debug.mouse_visibility)

    def apply_screen_shake(self):
        """Apply screen shake"""
        if self.shake > 0.1:
            shake_mod = int(self.shake * cfg.display.shake_intensity)
            screen.surface.scroll(
                randint(-shake_mod, shake_mod),
                randint(-shake_mod, shake_mod))
            self.shake *= 0.8

    def hud(self):
        """Draw HUD elements"""
        scoredisplay = f"Score {self.player_controller.score} | Difficulty {round(self.enemy_count, 1)}"
        if cfg.gameplay.wave_mode:
            scoredisplay += f"| Wave {self.wave}"
            if self.wave_mode_text_opacity > 0:
                screen.set_cached_text_alpha("wavemode", self.wave_mode_text_opacity)
                screen.display_cached_text("wavemode", self.wave_mode_text_x, self.wave_mode_text_y)
                self.wave_mode_text_x -= cfg.scroll_speed * (self.wave_mode_text_x / cfg.screen_width - 0.4)
                if self.wave_warmup_time <= 0:
                    self.wave_mode_text_opacity -= 2

        if cfg.debug.show_fps: scoredisplay += f" | FPS {round(screen.clock.get_fps())}"

        if cfg.easter_eggs.secret_option and screen.clock.get_fps() < 10: # Nothing to see here
            screen.render_text("How's your FPS looking??? :3", color="0xFFFFFF", opacity=64, x=10, y=cfg.screen_height//2, id="fps_easteregg")

        screen.render_text(scoredisplay, x=0, y=0)

    def update_entities(self):
        """Update all entities"""
        # Clear out any entities that are not alive
        self.entities = [entity for entity in self.entities if entity is not None and entity.alive]
        self.enemy_ai_danger_zones = []
        for entity in self.entities:
            entity.update()

    def spawn_new_enemies(self):
        """Try to spawn new enemies"""
        if self.wave_warmup_time:
            # Time between waves
            self.player_controller.entity.health += self.enemy_count * cfg.gameplay.wave_regen_multiplier # Slowly regen health
            self.wave_warmup_time -= 1
            if self.wave_warmup_time == 0:
                # Spawn new entities
                self.to_spawn = int(self.enemy_count)
                for i in range(self.to_spawn):
                    self.spawn_enemy(difficulty=int(self.enemy_count))
            return

        enemies_alive = len([enemy for enemy in self.entities if isinstance(enemy, Vehicle) and enemy.is_enemy]) # count number of enemies
        # Spawn all enemies in one go if cfg.gameplay.wave_mode is True, otherwise spawn one enemy to keep up with the count.
        if enemies_alive < int(self.enemy_count) and not cfg.gameplay.wave_mode:
            self.player_controller.entity.health += self.enemy_count * cfg.gameplay.enemy_regen_multiplier
            self.spawn_enemy(difficulty=int(self.enemy_count))

        elif enemies_alive == 0 and cfg.gameplay.wave_mode:
            self.player_controller.score += 50 * self.to_spawn
            print(f"Wave {self.wave} complete!")
            self.wave += 1
            self.wave_warmup_time = 120
            self.wave_mode_text_x = cfg.screen_width
            self.wave_mode_text_opacity = 255
            screen.render_text(f"Wave {self.wave}", display=False, id="wavemode")

    def spawn_enemy(self, sprite: pygame.Surface|None = None, difficulty: int = 1, moth: bool = False, type: int = 0):
        if (cfg.easter_eggs.moth_chance and random() <= cfg.easter_eggs.moth_chance) or moth:
            # Spawn moth and play music
            if cfg.easter_eggs.moth_music and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(f"./res/audio/moth.ogg", "music_moth")
                pygame.mixer.music.play(-1)
            aircraft.Moth(game=self, y=cfg.initial_aircraft_y, difficulty=difficulty)
        else:
            if type == 0: type = randint(1, min(5, difficulty))
            if sprite is not None: sprite = Sprite(sprite)
            aircraft.EnemyAircraft(game=self, y=cfg.initial_aircraft_y, sprite=sprite, difficulty=difficulty, ai_type=type)

def play():
    game = Game()
    game.begin()

    while game.running:
        game.loop()

    # Quit Pygame
    print(f"Final score: {game.player_controller.score}")
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    pygame.mixer.stop()
    pygame.mixer.music.stop()
