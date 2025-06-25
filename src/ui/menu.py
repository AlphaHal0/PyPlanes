import pygame
from sprite import Sprite
from ui.element import UIElement
from typing import Callable
from keybind import is_pressed
from config import kb
from display import screen
import math

ALIGN_NONE = 0 # does not automatically set element x/y (must be given manually)
ALIGN_LEFT = 1 # grids x/y to left
ALIGN_CENTERED = 2 # TODO

class Menu:
    """A class for a menu with a background and a list of elements"""
    def __init__(self, background: Sprite, elements: list[UIElement], on_close: Callable|None = None, grid_type: int = 0, mouse_effect: Sprite = None):
        self.grid_type = grid_type
        self.background = background
        self.elements = elements
        self.on_close = on_close
        self.any_listening = False
        self.run = True
        self.mouse_effect = mouse_effect
        self.mouse_effect_x = 0
        self.mouse_effect_y = 0
        self.mouse_effect_velocity_x = 0
        self.mouse_effect_velocity_y = 0
        self.mouse_effect_opacity = 0

    def distance_to(self, x: int, y: int) -> float:
        """Returns the distance from this Entity to (x, y)"""
        dx = abs(x - self.mouse_effect_x)**2
        dy = abs(y - self.mouse_effect_y)**2

        return math.sqrt(dx+dy)

    def tick(self):
        """Draw on screen and update contained elements."""
        self.background.draw(0, 0)

        mouse_pos = pygame.mouse.get_pos()
        if self.mouse_effect:
            # TODO: cleanup and remove magic numbers
            dx = mouse_pos[0] - self.mouse_effect_x
            dy = mouse_pos[1] - self.mouse_effect_y
            distance = self.distance_to(mouse_pos[0], mouse_pos[1])
            if distance > 50:
                self.mouse_effect_velocity_x += min(dx / distance * 1, 50)
                self.mouse_effect_velocity_y += min(dy / distance * 1, 50)

            self.mouse_effect_velocity_x *= 0.91
            self.mouse_effect_velocity_y *= 0.91

            self.mouse_effect_x += self.mouse_effect_velocity_x
            self.mouse_effect_y += self.mouse_effect_velocity_y

            self.mouse_effect.se
            self.mouse_effect.draw(self.mouse_effect_x-self.mouse_effect.size[0]//2, self.mouse_effect_y-self.mouse_effect.size[1]//2)

        # Check if any elements of this Menu are waiting for an input
        any_listening = False
        for element in self.elements:
            if element.listen_for_events:
                any_listening = True
                for event in pygame.event.get():
                    element.listen(event)

        release = False
        rrelease = False
        if not any_listening:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or is_pressed(event, kb.other.quit):
                    self.close()
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    release = True

                if event.type == pygame.MOUSEBUTTONUP and event.button == 3: # right click
                    rrelease = True

            click = pygame.mouse.get_pressed(3)[0]
            rclick = pygame.mouse.get_pressed(3)[2]
        else:
            click = False
            rclick = False

        for element in self.elements:
            element.update(mouse_x=mouse_pos[0], mouse_y=mouse_pos[1], click=click, release=release, rclick=rclick, rrelease=rrelease)

    def loop(self):
        """Starts an infinite loop where this will be updated and the screen will refresh every tick.
        Stops when the Quit button is pressed."""
        while self.run:
            self.tick()
            screen.update()

    def close(self):
        """Close menu"""
        self.run = False
        if self.on_close: self.on_close()

    def add_element(self, element: UIElement):
        self.elements.append(element)

    def __str__(self) -> str:
        return f"Menu running={self.run} listening={self.any_listening} element count={len(self.elements)}"
