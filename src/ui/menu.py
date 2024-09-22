import pygame
from sprite import Sprite
from ui.element import UIElement
from typing import Callable
import keybinds

class Menu:
    def __init__(self, background: Sprite, elements: list[UIElement], on_quit: Callable|None = None): 
        self.background = background
        self.elements = elements
        self.on_quit = on_quit

    def tick(self, screen: pygame.Surface):
        self.background.draw(screen, 0, 0)

        click = False
        release = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == keybinds.QUIT):
                self.on_quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
            if event.type == pygame.MOUSEBUTTONUP:
                release = True

        mouse_pos = pygame.mouse.get_pos()

        for element in self.elements:
            element.update(screen=screen, mouse_x=mouse_pos[0], mouse_y=mouse_pos[1], click=click, release=release)

        pygame.display.update()
