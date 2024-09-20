# To Create ENV: py -m venv env
# To Enter ENV: env/scripts/activate.ps1
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, INITIAL_AIRCRAFT_WIDTH, INITIAL_AIRCRAFT_HEIGHT, INITIAL_AIRCRAFT_X, INITIAL_AIRCRAFT_Y, SHOOT_COOLDOWN, INITIAL_HEALTH, INITIAL_ENEMY_AIRCRAFT, SCROLL_SPEED, WAVE_MODE, ENEMY_COUNT_INCREMENT, SHOW_FPS
import time

# Initialize Pygame
pygame.init()
pygame.font.init()
       
font = pygame.font.Font(size=50)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.mouse.set_visible(False)

from random import randint, choice
from classes import Aircraft, EnemyAircraft, Particle
from images import background_image, aircraft_image, enemy_image, large_explosions, small_explosions, moth_images

scroll_x = 0

player = Aircraft(INITIAL_AIRCRAFT_WIDTH, INITIAL_AIRCRAFT_HEIGHT, INITIAL_AIRCRAFT_X, INITIAL_AIRCRAFT_Y, aircraft_image, shoot_cooldown=SHOOT_COOLDOWN, health=INITIAL_HEALTH)
enemies = []
enemy_count = INITIAL_ENEMY_AIRCRAFT

def spawn_enemy(width = INITIAL_AIRCRAFT_WIDTH, height = INITIAL_AIRCRAFT_HEIGHT, image = enemy_image):
    enemies.append(EnemyAircraft(width, height, INITIAL_AIRCRAFT_Y, image, is_enemy = True))

for i in range(enemy_count):
    spawn_enemy()

# Game loop
bullets = []
particles = []
score = 0
spam_fire = False
wave = 1
running = True
framestart = time.time()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            new_bullet = player.shoot()
            if new_bullet is not None:
                bullets.append(new_bullet)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            new_bomb = player.bomb()
            if new_bomb is not None:
                bullets.append(new_bomb)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            spawn_enemy(INITIAL_AIRCRAFT_WIDTH * 5, INITIAL_AIRCRAFT_HEIGHT * 5, image=pygame.transform.scale(enemy_image, (INITIAL_AIRCRAFT_WIDTH * 5, INITIAL_AIRCRAFT_HEIGHT * 5)))
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            for enemy in enemies:
                enemy.fall()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
            if spam_fire:
                spam_fire = False
            else:
                spam_fire = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            particles.append(Particle(
                player.x, 
                player.y, 
                images=choice((large_explosions, small_explosions, moth_images)),
                duration=randint(60, 500)))

    if spam_fire:
        new_bullet = player.shoot()
        if new_bullet is not None:
            bullets.append(new_bullet)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        bullets.append(player.shoot())

    pygame.event.set_grab(True)

    # Update scrolling background
    scroll_x -= SCROLL_SPEED
    if scroll_x < -background_image.get_width():
        scroll_x = 0

    # Draw background
    screen.blit(background_image, (scroll_x, 0))
    screen.blit(background_image, (scroll_x + background_image.get_width(), 0))

    # Update aircraft position and check for collisions
    target_x, target_y = pygame.mouse.get_pos()
    player.apply_acceleration(target_x, target_y, trackable_distance=50)
    player.update_position()
    player.apply_friction()

    if player.ground_collision():
        print("Player hit the floor. Game over.")
        running = False

    if player.falling:
        particle = player.display_particle(images=small_explosions)
        if particle: particles.append(particle)

    enemies = [enemy for enemy in enemies if enemy.alive]
    for enemy in enemies:
        enemy.ai_tick()
        enemy.draw(screen)
        if enemy.ground_collision():
            enemy.destroy()
            particles.append(Particle(enemy.x, enemy.y, images=large_explosions, duration=400))
            score += 20 if WAVE_MODE else 70
            enemy_count += ENEMY_COUNT_INCREMENT
        if enemy.ai.shoot:
            bullets.append(enemy.shoot())
            enemy.ai.shoot -= 1
        if enemy.falling:
            particle = enemy.display_particle(images=small_explosions)
            if particle: particles.append(particle)

    # Spawn all enemies in one go if WAVE_MODE is True, otherwise spawn one enemy to keep up with the count.
    if (len(enemies) < int(enemy_count) and not WAVE_MODE) or (len(enemies) == 0 and WAVE_MODE):
        to_spawn = int(enemy_count) if WAVE_MODE else 1
        if WAVE_MODE: 
            score += 50 * to_spawn
            print(f"Wave {wave} complete!")
            wave += 1
        for i in range(to_spawn):
            spawn_enemy()

    # Update and draw bullets
    bullets = [bullet for bullet in bullets if bullet is not None and bullet.alive and 0 <= bullet.rect.x <= SCREEN_WIDTH]
    for bullet in bullets:
        bullet.update_position()

        if bullet.is_enemy:
            if bullet.is_colliding(player.rect):
                player.health -= 10
                player.check_health()
                bullet.destroy()
        else:
            collided_aircraft = bullet.is_colliding([enemy.rect for enemy in enemies])
            if collided_aircraft > -1:
                if enemies[collided_aircraft].fall(): score += 30
                bullet.destroy() # delete bullet
                
            # NOT EFFICIENT: I'm sure there's a better way than this
            for i in bullets:
                if bullet.is_colliding_entity(i): # Allow bullets to collide
                    particles.append(Particle(bullet.x+10, bullet.y, images=small_explosions, duration=100))
                    bullet.destroy()
                    i.destroy()
                
        bullet.draw(screen)

    particles = [particle for particle in particles if particle.alive]
    for particle in particles:
        particle.draw(screen)

    # Draw aircraft
    player.draw(screen)

    health_bar = pygame.Surface((150,10))
    health_bar.fill(0xFF0000)
    health_bar.fill(0x00FF00, rect=(0,0,(player.health/INITIAL_HEALTH)*150,10)),

    # Draw health bar
    screen.blit(
        health_bar,
        (player.x+(player.width//2-80),
         player.y-player.height)
    )

    
    scoredisplay = f"Score {score} | Difficulty {round(enemy_count, 1)}"
    if WAVE_MODE: scoredisplay += f"| Wave {wave}"
    if SHOW_FPS: scoredisplay += f" | FPS {round(1/(time.time() - framestart))}"
    scoredisplay_render = font.render(scoredisplay, False, (0, 0, 0))

    screen.blit(scoredisplay_render, (0, 0))

    # Update display
    framestart = time.time()
    pygame.display.update()
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
print(f"Final score: {score}")
quit()
