import json
import pygame

with open("etc/keymap.json", 'r') as _infile:
    keymap = json.load(_infile)

def is_pressed(event: pygame.event.Event, keycode: int, button_up: bool = False) -> bool:
    if button_up:
        if event == pygame.MOUSEBUTTONUP:
            return keycode == 1024 + event.button
        elif event.type == pygame.KEYUP:
            return keycode == event.key
        return False

    if event.type == pygame.MOUSEBUTTONDOWN:
        return keycode == 1024 + event.button
    elif event.type == pygame.KEYDOWN:
        return keycode == event.key
    
    return False
