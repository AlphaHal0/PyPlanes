# To Create ENV: py -m venv env
# To Enter ENV: env/scripts/activate.ps1
import pygame
from constants import *
from classes import Aircraft, Bullet, EnemyAircraft

# Initialize Pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.mouse.set_visible(False)

# Load background image
background_image = pygame.transform.scale(pygame.image.load("./assets/sky/side-scroll.jpg").convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
scroll_x = 0

bullet_image = pygame.image.load("./assets/bullets/Shot1.png").convert_alpha()
my_bullet = Bullet(INITIAL_BULLET_X, INITIAL_BULLET_Y)

aircraft_image = pygame.transform.scale(pygame.image.load("./assets/planes/player/spitfire.png").convert_alpha(),(SCREEN_WIDTH / 10, SCREEN_HEIGHT / 20) )
my_aircraft = Aircraft(INITIAL_AIRCRAFT_WIDTH, INITIAL_AIRCRAFT_HEIGHT, INITIAL_AIRCRAFT_X, INITIAL_AIRCRAFT_Y, aircraft_image)

sample_enemy = EnemyAircraft(INITIAL_AIRCRAFT_WIDTH, INITIAL_AIRCRAFT_HEIGHT, INITIAL_AIRCRAFT_Y, pygame.transform.flip(aircraft_image, True, False))

# Game loop
bullets = []
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
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

    if sample_enemy:
        sample_enemy.ai_tick()
        sample_enemy.draw(screen)
        if sample_enemy.ground_collision():
            sample_enemy = None
            print("Enemy hit the floor")
        if sample_enemy.ai.shoot:
            bullets.append(sample_enemy.shoot(True))
            sample_enemy.ai.shoot -= 1

    # Update and draw bullets
    bullets = [bullet for bullet in bullets if bullet is not None and 0 <= bullet.rect.x <= SCREEN_WIDTH]
    for bullet in bullets:
        bullet.update_position()
        bullet.draw(screen)

    # Draw aircraft
    my_aircraft.draw(screen)

    # Update display
    pygame.display.update()
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
quit()
