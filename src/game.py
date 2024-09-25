import pygame
import time
from config import cfg, kb
from random import random, randint, choice
import aircraft
from particle import Particle
from sprite import Sprite
from images import im
from keybind import is_pressed, is_held

# Game loop
def play(screen, font):
    if cfg.easter_eggs.moth_music_is_main_music:
        pygame.mixer.music.load(f"./res/audio/really_good_soundtrack.mp3", "music_moth")
        pygame.mixer.music.play(-1)

    enemies = []
    enemy_count = cfg.gameplay.initial_enemy_aircraft

    def spawn_enemy(image: pygame.Surface|None = None, difficulty: int = 1, moth: bool = False, type: int = 0):
        if (cfg.easter_eggs.moth_chance and random() <= cfg.easter_eggs.moth_chance) or moth:
            if cfg.easter_eggs.moth_music and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(f"./res/audio/really_good_soundtrack.mp3", "music_moth")
                pygame.mixer.music.play(-1)
            enemies.append(aircraft.Moth(cfg.initial_aircraft_y, difficulty))
        else:
            if type == 0: type = randint(1, min(5, difficulty))

            if image is None:
                match type:
                    case 1: image = im.aircraft.enemy_1
                    case 2: image = im.aircraft.enemy_2
                    case 3: image = im.aircraft.enemy_3
                    case 4: image = im.aircraft.enemy_4
                    case 5: image = im.aircraft.enemy_5
            enemies.append(aircraft.EnemyAircraft(cfg.initial_aircraft_y, Sprite(image), difficulty, ai_type=type))

    if not cfg.gameplay.wave_mode:
        for i in range(enemy_count):
            spawn_enemy()

    scroll_x = 0
    player = aircraft.Aircraft(
        cfg.initial_aircraft_x, 
        cfg.initial_aircraft_y if cfg.gameplay.disable_takeoff else cfg.floor_y - im.aircraft.aircraft.get_height(), 
        Sprite(im.aircraft.aircraft), 
        shoot_cooldown=cfg.gameplay.player_shoot_cooldown, 
        bomb_cooldown=cfg.gameplay.player_bomb_cooldown, 
        health=cfg.gameplay.initial_health)
    enemies = []
    enemy_count = cfg.gameplay.initial_enemy_aircraft
    scroll_x = 0
    bullets = []
    particles = []
    enemy_ai_danger_zones = []
    score = 0
    wave = 1
    wave_mode_text_x = cfg.screen_width
    wave_mode_text_y = cfg.screen_height // 2 - font.get_height() // 2
    running = True
    game_paused = False
    frame_step = 0
    framestart = time.time()

    if cfg.gameplay.disable_takeoff:
        # Set initial values for when not taking off
        wave_warmup_time = 120 if cfg.gameplay.wave_mode else 0
        wave_mode_text_opacity = 255
        scroll_speed = cfg.scroll_speed
        pregame_timer = 0
        wave_mode_text_opacity = 255
        pygame.mouse.set_visible(cfg.debug.mouse_visibility)
    else:
        # Set initial values for taking off
        wave_warmup_time = 0
        pregame_timer = 300
        scroll_speed = 0
        wave_mode_text_opacity = 0
    while running:
        # Draw background
        screen.blit(im.background.background, (scroll_x, 0))
        screen.blit(im.background.background, (scroll_x + im.background.background.get_width(), 0))

        # Update scrolling background
        scroll_x -= scroll_speed
        if scroll_x < -im.background.background.get_width():
            scroll_x = 0

        if pregame_timer == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or is_pressed(event, kb.other.quit):
                    running = False
                elif is_pressed(event, kb.weapons.shoot):
                    new_bullet = player.shoot()
                    if new_bullet is not None:
                        bullets.append(new_bullet)
                elif is_pressed(event, kb.weapons.bomb):
                    new_bomb = player.bomb()
                    if new_bomb is not None:
                        bullets.append(new_bomb)
                elif is_pressed(event, kb.debug.spawn_enemy):
                    while True:
                        event = pygame.event.wait()
                        if event.type == pygame.KEYDOWN:
                            match event.key:
                                case kb.debug.spawn_enemy_ai_1: spawn_enemy(difficulty=int(enemy_count), type=1)
                                case kb.debug.spawn_enemy_ai_2: spawn_enemy(difficulty=int(enemy_count), type=2)
                                case kb.debug.spawn_enemy_ai_3: spawn_enemy(difficulty=int(enemy_count), type=3)
                                case kb.debug.spawn_enemy_ai_4: spawn_enemy(difficulty=int(enemy_count), type=4)
                                case kb.debug.spawn_enemy_ai_5: spawn_enemy(difficulty=int(enemy_count), type=5)

                            break
                            
                elif is_pressed(event, kb.debug.spawn_moth):
                    spawn_enemy(moth=True, difficulty=int(enemy_count))
                elif is_pressed(event, kb.debug.kill_all):
                    for enemy in enemies:
                        enemy.fall()
                elif is_pressed(event, kb.debug.spawn_particle):
                    particles.append(Particle(
                        player.x, 
                        player.y, 
                        sprite=choice((Sprite(im.particle.large_explosions), Sprite(im.particle.small_explosions), Sprite(im.aircraft.moth))),
                        duration=randint(10, 100),
                        scale=randint(1,5),
                        adjust_pos=False))
                elif is_pressed(event, kb.debug.pause_game):
                    print("Game paused")
                    game_paused = not game_paused
                    
                # pitch
                elif is_pressed(event, kb.movement.pitch_up):
                    player.set_pitch(20)
                elif is_pressed(event, kb.movement.pitch_down):
                    player.set_pitch(-20)
                elif is_pressed(event, kb.movement.pitch_down, True) or is_pressed(event, kb.movement.pitch_up, True):
                    player.set_pitch(0)

            pygame.event.set_grab(True)

            if is_held(kb.weapons.shoot_hold):
                new_bullet = player.shoot()
                if new_bullet is not None:
                    bullets.append(new_bullet)

            # Update aircraft position and check for collisions
            target_x, target_y = pygame.mouse.get_pos()
            player.apply_acceleration(target_x, target_y, trackable_distance=50)
            player.update()

            if not cfg.debug.invincible: player.check_health()

            if player.ground_collision():
                player.health -= cfg.gameplay.ground_health_decay
                if not cfg.debug.invincible and player.health <= 0:
                    print("Player hit the floor. Game over.")
                    running = False
                particle = player.display_particle(Sprite(im.particle.small_explosions, animation_time=30, size_multiplier=2), 100)
                if particle: particles.append(particle)

            if player.falling:
                particle = player.display_particle(Sprite(im.particle.small_explosions, animation_time=5))
                if particle: particles.append(particle)

            enemies = [enemy for enemy in enemies if enemy.alive]
            for enemy in enemies:
                enemy.ai_tick(danger_zones=enemy_ai_danger_zones, player_y=player.y, player_x=player.x, enemy_y=enemy.y)
                enemy.draw(screen)
                if enemy.ground_collision():
                    enemy.destroy()
                    particles.append(Particle(enemy.x, enemy.y, sprite=Sprite(im.particle.large_explosions, animation_time=40), scale=3, adjust_pos=False, move_with_screen=True))
                    score += 20 if cfg.gameplay.wave_mode else 70
                    enemy_count += cfg.gameplay.enemy_count_increment
                if enemy.ai.shoot:
                    bullets.append(enemy.shoot())
                    enemy.ai.shoot -= 1
                if enemy.falling:
                    particle = enemy.display_particle(Sprite(im.particle.small_explosions, animation_time=5))
                    if particle: particles.append(particle)

                if cfg.debug.show_ai_type:
                    ai_marker = pygame.Surface((10,10))
                    ai_marker.fill(enemy.ai.debug_color)
                    screen.blit(ai_marker, (enemy.x+enemy.sprite.size[0], enemy.y))

            if wave_warmup_time:
                player.health += enemy_count * cfg.gameplay.wave_regen_multiplier
                wave_warmup_time -= 1
                if wave_warmup_time == 0:
                    to_spawn = int(enemy_count)
                    for i in range(to_spawn):
                        spawn_enemy(difficulty=int(enemy_count))

            # Spawn all enemies in one go if cfg.gameplay.wave_mode is True, otherwise spawn one enemy to keep up with the count.
            elif len(enemies) < int(enemy_count) and not cfg.gameplay.wave_mode:
                player.health += enemy_count * cfg.gameplay.enemy_regen_multiplier
                spawn_enemy(difficulty=int(enemy_count))

            elif len(enemies) == 0 and cfg.gameplay.wave_mode:
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
                bullet.update()

                if bullet.is_enemy:
                    if bullet.is_colliding(player.rect):
                        player.health -= 10
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
            for event in pygame.event.get():
                if event.type == pygame.QUIT or is_pressed(event, kb.other.quit):
                    running = False

            if pregame_timer > 100:
                scroll_speed = int(((300-pregame_timer)/200) * cfg.scroll_speed)
            else:
                player.apply_acceleration(cfg.initial_aircraft_x, cfg.initial_aircraft_y)
                player.update()

            pregame_timer -= 1

            if pregame_timer == 0:
                wave_warmup_time = 120 if cfg.gameplay.wave_mode else 0
                wave_mode_text_opacity = 255
                scroll_speed = cfg.scroll_speed
                pygame.mouse.set_visible(cfg.debug.mouse_visibility)


        particles = [particle for particle in particles if particle.alive]
        for particle in particles:
            particle.draw(screen)

        # Draw aircraft
        player.draw(screen)

        health_bar = pygame.Surface((150,10))
        health_bar.fill(0xFF0000)
        health_bar.fill(0x00FF00, rect=(0,0,(player.health/cfg.gameplay.initial_health)*150,10)),

        # Draw health bar
        screen.blit(
            health_bar,
            (player.x+(player.width//2-80),
            player.y-player.height)
        )
        
        scoredisplay = f"Score {score} | Difficulty {round(enemy_count, 1)}"
        if cfg.gameplay.wave_mode: 
            scoredisplay += f"| Wave {wave}"
            if wave_mode_text_opacity > 0:
                wavemodedisplay = font.render(f"Wave {wave}", False, 0)
                wavemodedisplay.set_alpha(wave_mode_text_opacity)
                screen.blit(wavemodedisplay, (wave_mode_text_x, wave_mode_text_y))
                wave_mode_text_x -= cfg.scroll_speed * (wave_mode_text_x / cfg.screen_width - 0.4)
                if wave_warmup_time <= 0:
                    wave_mode_text_opacity -= 2

        if cfg.debug.show_fps: scoredisplay += f" | FPS {round(1/(time.time() - framestart))}"
        scoredisplay_render = font.render(scoredisplay, False, 0)

        screen.blit(scoredisplay_render, (0, 0))

        while game_paused and not frame_step:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                elif is_pressed(event, kb.debug.pause_game) or is_pressed(event, kb.other.quit): 
                    game_paused = False
                    print("Game resumed")
                elif is_pressed(event, kb.debug.step_one_frame):
                    frame_step = 1
                    break
                elif is_pressed(event, kb.debug.step_5_frames):
                    frame_step = 5
                    break
                elif is_pressed(event, kb.debug.step_60_frames):
                    frame_step = 60
                    break

        if frame_step: frame_step -= 1

        # Update display
        framestart = time.time()
        pygame.display.update()
        pygame.time.Clock().tick(60)

    # Quit Pygame
    print(f"Final score: {score}")
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    pygame.mixer.stop()
    pygame.mixer.music.stop()
