#!/usr/bin/env python

import pygame

PASTELS = {
    'red': (255, 128, 128),
    'blue': (120, 155, 239),
    'green': (109, 209, 105),
    'purple': (205, 102, 192),
    'aqua': (93, 185, 170),
    'orange': (243, 187, 122)
}

class Renderer(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([1600, 900], pygame.FULLSCREEN)
        
    def clear(self, color=PASTELS['blue']):
        self.screen.fill(color)
        
    def loop(self, input):
        self.clear()
        return self.screen
        
    def display(self):
        pygame.display.flip()
        
def input_debug_shim(screen, input):
    font = pygame.font.Font(None, 30)
    positions = input.get_pos()
    
    def display(pos, x_offset):
        for i, coord in enumerate(pos):
            screen.blit(
                font.render(str(coord), True, (255, 255, 255)),
                (10 + x_offset * 300, 10 + i * 40)
            )
    
    for i, position in enumerate(positions):
        display(position, i)
        
    return screen
    
def display_pointer_circles(screen, input):
    positions = input.get_pos()
    for position in positions:
        x, y, z = position
        pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), 20)
    return screen