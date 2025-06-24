# type checking without circular import
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game
    from aircraft import Aircraft

import pygame
from random import randint, choice
from sprite import Sprite
from config import cfg, kb
from images import im
from keybind import is_pressed, is_held
from ground_vehicle import GroundVehicle
from particle import Particle
from vfx import ScreenDistortion

class PlayerController:
    """Class to manage an entity controlled by a player"""
    def __init__(self, game: Game, entity: Aircraft):
        self.game = game
        self.entity = entity

    def update(self):
        """Update aircraft position and check for collisions"""
        self.process_inputs()

        game = self.game
        entity = self.entity

        target_x, target_y = pygame.mouse.get_pos()
        entity.apply_acceleration(target_x, target_y, trackable_distance=50)

        if not cfg.debug.invincible: entity.check_health()

        if entity.falling:
            entity.spawn_particle(Sprite(im.particle.small_explosions, animation_time=5))
            game.shake = 2

        if entity.ground_collision():
            entity.health -= cfg.gameplay.ground_health_decay
            if not cfg.debug.invincible and entity.health <= 0:
                print("Player hit the floor. Game over.")
                game.running = False
            particle = entity.spawn_particle(Sprite(im.particle.small_explosions, animation_time=30, size_multiplier=2), 100)
            if particle:
                game.shake = 8

    def process_inputs(self):
        """Process keyboard and mouse inputs"""
        # TODO: abstract control handling
        game = self.game
        entity = self.entity

        for event in pygame.event.get():
            if event.type == pygame.QUIT or is_pressed(event, kb.other.quit):
                game.running = False
            elif is_pressed(event, kb.weapons.shoot):
                entity.shoot()
            elif is_pressed(event, kb.weapons.bomb):
                entity.bomb()
            elif is_pressed(event, kb.weapons.rocket):
                entity.drop_rocket()
            elif is_pressed(event, kb.debug.spawn_enemy):
                while True:
                    event = pygame.event.wait()
                    if event.type == pygame.KEYDOWN:
                        match event.key:
                            case kb.debug.spawn_enemy_ai_1: game.spawn_enemy(difficulty=int(game.enemy_count), type=1)
                            case kb.debug.spawn_enemy_ai_2: game.spawn_enemy(difficulty=int(game.enemy_count), type=2)
                            case kb.debug.spawn_enemy_ai_3: game.spawn_enemy(difficulty=int(game.enemy_count), type=3)
                            case kb.debug.spawn_enemy_ai_4: game.spawn_enemy(difficulty=int(game.enemy_count), type=4)
                            case kb.debug.spawn_enemy_ai_5: game.spawn_enemy(difficulty=int(game.enemy_count), type=5)

                        break

            elif is_pressed(event, kb.debug.spawn_ground_enemy):
                GroundVehicle()

            elif is_pressed(event, kb.debug.spawn_moth):
                game.spawn_enemy(moth=True, difficulty=int(game.enemy_count))
            # elif is_pressed(event, kb.debug.kill_all):
            #     for enemy in game.enemies:
            #         enemy.hit()
            elif is_pressed(event, kb.debug.spawn_particle):
                Particle(
                    entity.x,
                    entity.y,
                    sprite=choice((Sprite(im.particle.large_explosions), Sprite(im.particle.small_explosions), Sprite(im.aircraft.moth))),
                    duration=randint(10, 100),
                    scale=randint(1,5),
                    adjust_pos=False)
            elif is_pressed(event, kb.debug.shockwave):
                ScreenDistortion(game=game, x=entity.x+entity.width//2, y=entity.y+-entity.height//2, velocity=50, direction=entity.pitch, angle=360, width=10, time_alive=20)

            elif is_pressed(event, kb.debug.pause_game):
                print("Game paused")
                game.game_paused = not game.game_paused

            # pitch
            elif is_pressed(event, kb.movement.pitch_up):
                entity.set_pitch(20)
            elif is_pressed(event, kb.movement.pitch_down):
                entity.set_pitch(-20)
            elif is_pressed(event, kb.movement.pitch_down, True) or is_pressed(event, kb.movement.pitch_up, True):
                entity.set_pitch(0)

        pygame.event.set_grab(True)

        if is_held(kb.weapons.shoot_hold):
            entity.shoot()

        if is_held(kb.debug.thrust):
            Particle(
                entity.x + entity.width * 0.3,
                entity.y + entity.height * 0.5,
                sprite=Sprite(im.particle.afterburner),
                scale=1,
                velocity_x=-40,
                move_with_screen=True,
                rotation=entity.pitch,
                adj_velocity_for_rot=True
            )
            if game.scroll_speed < cfg.scroll_speed * 2:
                game.scroll_speed += 0.2

            game.shake = (game.scroll_speed - cfg.scroll_speed) / cfg.scroll_speed * 5
        else:
            if game.scroll_speed > cfg.scroll_speed:
                game.scroll_speed -= 0.2
