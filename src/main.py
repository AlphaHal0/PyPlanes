# To Create ENV: py -m venv env
# To Enter ENV: env/scripts/activate.ps1
import pygame
import keybinds
import time
from config import cfg

# Initialize Pygame
pygame.init()
pygame.font.init()
       
font = pygame.font.Font(size=50)
# Set up the screen
screen = pygame.display.set_mode((cfg.screen_width, cfg.screen_height))

from random import random, randint, choice
import aircraft
from particle import Particle
from sprite import Sprite
import images as im

scroll_x = 0
player = aircraft.Aircraft(
    cfg.initial_aircraft_x, 
    cfg.initial_aircraft_y if cfg.disable_takeoff else cfg.floor_y, 
    Sprite(im.aircraft_image), 
    shoot_cooldown=cfg.player_shoot_cooldown, 
    bomb_cooldown=cfg.player_bomb_cooldown, 
    health=cfg.initial_health)
enemies = []
enemy_count = cfg.initial_enemy_aircraft

if cfg.moth_music_is_main_music:
    pygame.mixer.music.load(f"{cfg.asset_folder}/easteregg/really_good_soundtrack.mp3", "music_moth")
    pygame.mixer.music.play(-1)

def spawn_enemy(image: pygame.Surface = im.enemy_image, difficulty: float = 1, moth: bool = False):
    if (cfg.moth_chance and random() <= cfg.moth_chance) or moth:
        if cfg.moth_music and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(f"{cfg.asset_folder}/easteregg/really_good_soundtrack.mp3", "music_moth")
            pygame.mixer.music.play(-1)
        enemies.append(aircraft.Moth(cfg.initial_aircraft_y, int(difficulty)))
    else:
        enemies.append(aircraft.EnemyAircraft(cfg.initial_aircraft_y, Sprite(image), int(difficulty)))

if not cfg.wave_mode:
    for i in range(enemy_count):
        spawn_enemy()

# Game loop
bullets = []
particles = []
enemy_ai_danger_zones = []
score = 0
spam_fire = False
wave = 1
wave_mode_text_x = cfg.screen_width
wave_mode_text_y = cfg.screen_height // 2 - font.get_height() // 2
running = True
framestart = time.time()

if cfg.disable_takeoff:
    wave_warmup_time = 120 if cfg.wave_mode else 0
    wave_mode_text_opacity = 255
    scroll_speed = cfg.scroll_speed
    pregame_timer = 0
    wave_mode_text_opacity = 255
    pygame.mouse.set_visible(cfg.mouse_visibility)
else:
    wave_warmup_time = 0
    pregame_timer = 300
    scroll_speed = 0
    wave_mode_text_opacity = 0
while running:
    # Draw background
    screen.blit(im.background_image, (scroll_x, 0))
    screen.blit(im.background_image, (scroll_x + im.background_image.get_width(), 0))

    # Update scrolling background
    scroll_x -= scroll_speed
    if scroll_x < -im.background_image.get_width():
        scroll_x = 0

    if pregame_timer == 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == keybinds.QUIT):
                running = False
            elif event.type == keybinds.SHOOT and event.button == 1:  # Left mouse button
                new_bullet = player.shoot()
                if new_bullet is not None:
                    bullets.append(new_bullet)
            elif event.type == pygame.KEYDOWN and event.key == keybinds.SHOOT_2:
                new_bullet = player.shoot()
                if new_bullet is not None:
                    bullets.append(new_bullet)
            elif event.type == pygame.KEYDOWN and event.key == keybinds.BOMB:
                new_bomb = player.bomb()
                if new_bomb is not None:
                    bullets.append(new_bomb)
            elif event.type == pygame.KEYDOWN and event.key == keybinds.DEBUG_SPAWN_ENEMY:
                spawn_enemy(difficulty=enemy_count)
            elif event.type == pygame.KEYDOWN and event.key == keybinds.DEBUG_SPAWN_MOTH:
                spawn_enemy(moth=True, difficulty=enemy_count)
            elif event.type == pygame.KEYDOWN and event.key == keybinds.DEBUG_KILL_ALL:
                for enemy in enemies:
                    enemy.fall()
            elif event.type == pygame.KEYDOWN and event.key == keybinds.DEBUG_RAPID_FIRE:
                if spam_fire:
                    spam_fire = False
                else:
                    spam_fire = True
            elif event.type == pygame.KEYDOWN and event.key == keybinds.DEBUG_SPAWN_PARTICLE:
                particles.append(Particle(
                    player.x, 
                    player.y, 
                    sprite=choice((Sprite(im.large_explosions), Sprite(im.small_explosions), Sprite(im.moth_images))),
                    duration=randint(10, 100),
                    scale=randint(1,5),
                    adjust_pos=False))
                
            # pitch
            elif event.type == pygame.KEYDOWN and event.key == keybinds.PITCH_UP:
                player.set_pitch(20)
            elif event.type == pygame.KEYDOWN and event.key == keybinds.PITCH_DOWN:
                player.set_pitch(-20)
            elif event.type == pygame.KEYUP and (event.key == keybinds.PITCH_UP or event.key == keybinds.PITCH_DOWN):
                player.set_pitch(0)

        if spam_fire:
            new_bullet = player.shoot()
            if new_bullet is not None:
                bullets.append(new_bullet)

        keys = pygame.key.get_pressed()
        if keys[keybinds.RAPID_FIRE]:
            bullets.append(player.shoot())

        pygame.event.set_grab(True)

        # Update aircraft position and check for collisions
        target_x, target_y = pygame.mouse.get_pos()
        player.apply_acceleration(target_x, target_y, trackable_distance=50)
        player.update_position()
        player.apply_friction()

        if player.ground_collision() and not cfg.debug_invincible:
            print("Player hit the floor. Game over.")
            running = False

        if player.falling:
            particle = player.display_particle(Sprite(im.small_explosions))
            if particle: particles.append(particle)

        enemies = [enemy for enemy in enemies if enemy.alive]
        for enemy in enemies:
            enemy.ai_tick(danger_zones=enemy_ai_danger_zones, player_y=player.y)
            enemy.draw(screen)
            if enemy.ground_collision():
                enemy.destroy()
                particles.append(Particle(enemy.x, enemy.y, sprite=Sprite(im.large_explosions), duration=40, scale=3, adjust_pos=False))
                score += 20 if cfg.wave_mode else 70
                enemy_count += cfg.enemy_count_increment
            if enemy.ai.shoot:
                bullets.append(enemy.shoot())
                enemy.ai.shoot -= 1
            if enemy.falling:
                particle = enemy.display_particle(Sprite(im.small_explosions))
                if particle: particles.append(particle)

            if cfg.show_ai_type:
                ai_marker = pygame.Surface((10,10))
                ai_marker.fill(enemy.ai.debug_color)
                screen.blit(ai_marker, (enemy.x+enemy.sprite.size[0], enemy.y))

        # Spawn all enemies in one go if cfg.wave_mode is True, otherwise spawn one enemy to keep up with the count.
        if wave_warmup_time:
            wave_warmup_time -= 1
            if wave_warmup_time == 0:
                to_spawn = int(enemy_count)
                for i in range(to_spawn):
                    spawn_enemy(difficulty=enemy_count)

        elif len(enemies) < int(enemy_count) and not cfg.wave_mode:
            spawn_enemy(difficulty=enemy_count)

        elif len(enemies) == 0 and cfg.wave_mode:
            score += 50 * to_spawn
            print(f"Wave {wave} complete!")
            wave += 1
            wave_warmup_time = 120
            wave_mode_text_x = cfg.screen_width
            wave_mode_text_opacity = 255

        # Update and draw bullets
        bullets = [bullet for bullet in bullets if bullet is not None and bullet.alive and 0 <= bullet.rect.x <= cfg.screen_width]
        enemy_ai_danger_zones = []
        for bullet in bullets:
            bullet.update_position()

            if bullet.is_enemy:
                if bullet.is_colliding(player.rect):
                    player.health -= 10
                    if not cfg.debug_invincible: player.check_health()
                    particles.append(bullet.explode(enemies))
            else:
                collided_aircraft = bullet.is_colliding([enemy.rect for enemy in enemies])
                if collided_aircraft > -1:
                    if enemies[collided_aircraft].fall(): score += 30
                    particles.append(bullet.explode(enemies)) # delete bullet
                    
                # NOT EFFICIENT: I'm sure there's a better way than this
                for i in bullets:
                    if bullet.is_colliding_entity(i): # Allow bullets to collide
                        particles.append(bullet.explode(enemies))
                        i.explode()

                enemy_ai_danger_zones.append(bullet.y)

            if bullet.ground_collision():
                particles.append(bullet.explode(enemies))
                    
            bullet.draw(screen)

    else:
        if pregame_timer > 100:
            scroll_speed = int(((300-pregame_timer)/200) * cfg.scroll_speed)
        else:
            player.apply_acceleration(cfg.initial_aircraft_x, cfg.initial_aircraft_y)
            player.update_position()
            player.apply_friction()

        pregame_timer -= 1

        if pregame_timer == 0:
            wave_warmup_time = 120 if cfg.wave_mode else 0
            wave_mode_text_opacity = 255
            scroll_speed = cfg.scroll_speed
            pygame.mouse.set_visible(cfg.mouse_visibility)


    particles = [particle for particle in particles if particle.alive]
    for particle in particles:
        particle.draw(screen)

    # Draw aircraft
    player.draw(screen)

    health_bar = pygame.Surface((150,10))
    health_bar.fill(0xFF0000)
    health_bar.fill(0x00FF00, rect=(0,0,(player.health/cfg.initial_health)*150,10)),

    # Draw health bar
    screen.blit(
        health_bar,
        (player.x+(player.width//2-80),
         player.y-player.height)
    )
    
    scoredisplay = f"Score {score} | Difficulty {round(enemy_count, 1)}"
    if cfg.wave_mode: 
        scoredisplay += f"| Wave {wave}"
        if wave_mode_text_opacity > 0:
            wavemodedisplay = font.render(f"Wave {wave}", False, 0)
            wavemodedisplay.set_alpha(wave_mode_text_opacity)
            screen.blit(wavemodedisplay, (wave_mode_text_x, wave_mode_text_y))
            wave_mode_text_x -= cfg.scroll_speed * (wave_mode_text_x / cfg.screen_width - 0.4)
            if wave_warmup_time <= 0:
                wave_mode_text_opacity -= 2

    if cfg.show_fps: scoredisplay += f" | FPS {round(1/(time.time() - framestart))}"
    scoredisplay_render = font.render(scoredisplay, False, 0)

    screen.blit(scoredisplay_render, (0, 0))

    # Update display
    framestart = time.time()
    pygame.display.update()
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
print(f"Final score: {score}")
quit()
