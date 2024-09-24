import pygame
from sprite import Sprite
from ui.element import UIElement
from typing import Callable
from keybind import is_pressed
from config import kb

ALIGN_NONE = 0 # does not automatically set element x/y (must be given manually)
ALIGN_LEFT = 1 # grids x/y to left
ALIGN_CENTERED = 2 # [TODO]

class Menu:
    """A class for a menu with a background and a list of elements"""
    def __init__(self, background: Sprite, elements: list[UIElement], on_quit: Callable|None = None, grid_type: int = 0):
        self.grid_type = grid_type
        self.background = background
        self.elements = elements
        self.on_quit = on_quit
        self.any_listening = False
        self.run = True

    def tick(self, screen: pygame.Surface):
        """Draw on screen and update contained elements."""
        self.background.draw(screen, 0, 0)

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
                    self.run = False
                    if self.on_quit: self.on_quit()

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    release = True

                if event.type == pygame.MOUSEBUTTONUP and event.button == 3: # right click
                    rrelease = True

            click = pygame.mouse.get_pressed(3)[0]
            rclick = pygame.mouse.get_pressed(3)[2]
        else:
            click = False
            rclick = False

        mouse_pos = pygame.mouse.get_pos()

        for element in self.elements:
            element.update(screen=screen, mouse_x=mouse_pos[0], mouse_y=mouse_pos[1], click=click, release=release, rclick=rclick, rrelease=rrelease)

        pygame.display.update()

    def loop(self, screen: pygame.Surface):
        """Starts an infinite loop where this will be updated and the screen will refresh every tick.
        Stops when the Quit button is pressed."""
        while self.run:
            self.tick(screen)
            pygame.display.update()
            pygame.time.Clock().tick(60)

    def add_element(self, element: UIElement):
        self.elements.append(element)

    def __str__(self) -> str:
        return f"Menu running={self.run} listening={self.any_listening} element count={len(self.elements)}"
