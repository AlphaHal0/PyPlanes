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

def is_held(keycode: int) -> bool:
    if 1024 < keycode < 1030: # is mouse button
        return pygame.mouse.get_pressed()[keycode-1025]
    else:
        return pygame.key.get_pressed()[keycode]
