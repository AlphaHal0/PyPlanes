# To Create ENV: py -m venv env
# To Enter ENV: env/scripts/activate.ps1
import pygame
from constants import *
from classes import Aircraft, Bullet, EnemyAircraft

# Initialize Pygame
pygame.init()
pygame.font.init()

font = pygame.font.Font(size=50)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.mouse.set_visible(False)

# Load background image
background_image = pygame.transform.scale(pygame.image.load("./assets/sky/side-scroll.jpg").convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
scroll_x = 0

bullet_image = pygame.image.load("./assets/bullets/Shot1.png").convert_alpha()
my_bullet = Bullet(INITIAL_BULLET_X, INITIAL_BULLET_Y)

aircraft_image = pygame.transform.scale(pygame.image.load("./assets/planes/player/spitfire.png").convert_alpha(),(SCREEN_WIDTH / 10, SCREEN_HEIGHT / 20) )
enemy_aircraft_image = pygame.transform.scale(pygame.image.load("./assets/planes/enemies/enemy_lvl_1.png").convert_alpha(),(SCREEN_WIDTH / 10, SCREEN_HEIGHT / 20) )
my_aircraft = Aircraft(INITIAL_AIRCRAFT_WIDTH, INITIAL_AIRCRAFT_HEIGHT, INITIAL_AIRCRAFT_X, INITIAL_AIRCRAFT_Y, aircraft_image, shoot_cooldown=SHOOT_COOLDOWN)
enemies = []
enemy_count = INITIAL_ENEMY_AIRCRAFT

def spawn_enemy(width = INITIAL_AIRCRAFT_WIDTH, height = INITIAL_AIRCRAFT_HEIGHT, image = enemy_aircraft_image):
    enemies.append(EnemyAircraft(width, height, INITIAL_AIRCRAFT_Y, image, is_enemy = True))

for i in range(enemy_count):
    spawn_enemy()

# Game loop
bullets = []
score = 0
lives = INITIAL_LIVES
spam_fire = False
wave = 1
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            new_bullet = my_aircraft.shoot()
            if new_bullet is not None:
                bullets.append(new_bullet)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            spawn_enemy(INITIAL_AIRCRAFT_WIDTH * 5, INITIAL_AIRCRAFT_HEIGHT * 5, image=pygame.transform.scale(enemy_aircraft_image, (INITIAL_AIRCRAFT_WIDTH * 5, INITIAL_AIRCRAFT_HEIGHT * 5)))
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            for enemy in enemies:
                enemy.fall()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
            if spam_fire:
                spam_fire = False
            else:
                spam_fire = True

    if spam_fire:
        new_bullet = my_aircraft.shoot()
        if new_bullet is not None:
            bullets.append(new_bullet)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        bullets.append(my_aircraft.shoot())

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
    my_aircraft.apply_acceleration(target_x, target_y, trackable_distance=50)
    my_aircraft.update_position()
    my_aircraft.apply_friction()

    if my_aircraft.ground_collision():
        print("Player hit the floor. Game over.")
        running = False

    enemies = [enemy for enemy in enemies if enemy.alive]
    for enemy in enemies:
        enemy.ai_tick()
        enemy.draw(screen)
        if enemy.ground_collision():
            enemy.destroy()
            score += 20 if WAVE_MODE else 70
            enemy_count += ENEMY_COUNT_INCREMENT
        if enemy.ai.shoot:
            bullets.append(enemy.shoot(True))
            enemy.ai.shoot -= 1

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
            if bullet.is_colliding(my_aircraft.rect):
                lives -= 1
                if lives <= 0: my_aircraft.fall()
                bullet.destroy()
        else:
            collided_aircraft = bullet.is_colliding([enemy.rect for enemy in enemies])
            if collided_aircraft > -1:
                if enemies[collided_aircraft].fall(): score += 30
                bullet.destroy() # delete bullet

        bullet.draw(screen)

    # Draw aircraft
    my_aircraft.draw(screen)

    scoredisplay = f"Lives {lives} | Score {score} | Difficulty {round(enemy_count, 1)} "
    if WAVE_MODE: scoredisplay += f"| Wave {wave}"
    scoredisplay_render = font.render(scoredisplay, False, (0, 0, 0))

    screen.blit(scoredisplay_render, (0, 0))

    # Update display
    pygame.display.update()
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
print(f"Final score: {score}")
quit()
