import pygame
from ui.button import Button
from config import cfg
from sprite import Sprite
from ui.element import UIElement

# Lambda function to get font
get_font = lambda s: pygame.font.Font(s)

class Menu:
    def __init__(self, background: Sprite, elements: list[UIElement]): 
        self.background = background
        self.elements = elements

    def tick(self, screen: pygame.Surface):
        self.background.draw(screen, 0, 0)

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        screen.blit(MENU_TEXT, MENU_RECT)

        for element in self.elements:
            element.update()

        pygame.display.update()
