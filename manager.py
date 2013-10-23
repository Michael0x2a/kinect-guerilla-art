#!/usr/bin/env python

import telemetry
import interactions
import input_processors
import rendering

import pygame

class ChangeInteraction(Exception):
    def __init__(self, *arg, **kwargs):
        super(ChangeInteraction, self).__init__(*args, **kwargs)
        

class Manager(object):
    def __init__(self, sequences, start, input):
        self.sequences = sequences
        self.input = input
        self.current = self.sequences[start](self.input)
        self.renderer = rendering.Renderer()
        self.timer = pygame.time.Clock()
        telemetry.log('Starting.')
        self.inactive_start = 0
        self.refresh = 0
        
    def mainloop(self):
        previous = None
        while True:
            screen = self.renderer.loop(self.input)
            
            screen, next_interaction = self.current.loop(screen)
            
            if self.current.active:
                self.inactive_start = pygame.time.get_ticks()
            delta = pygame.time.get_ticks() - self.inactive_start
            if delta > 5000:
                next_interaction = 'Sad'
            if self.input.too_close():
                next_interaction = "Scared"
            if pygame.time.get_ticks() - self.refresh > 10000:
                self.refresh = pygame.time.get_ticks()
                self.input.ignore_list = []
            
            if next_interaction is not None:
                telemetry.log('Switching state: ' + next_interaction)
                if next_interaction == 'Scared':
                    self.current = self.sequences[next_interaction](self.input, previous)
                else:
                    self.current = self.sequences[next_interaction](self.input)
                if next_interaction != 'Scared':
                    previous = next_interaction
                
            
            #screen = rendering.input_debug_shim(screen, self.input)
            screen = rendering.display_pointer_circles(screen, self.input)
            self.renderer.display()
            
            self.keep_alive()
            
    def keep_alive(self):
        self.timer.tick(30)
        event = pygame.event.poll()
        
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit(0)
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_p]:
                pygame.quit()
                raise SystemExit(0)
                
        
        
if __name__ == '__main__':
    manager = Manager(
        interactions.INTERACTIONS, 
        'Lonely', 
        #input_processors.Mouse())
        input_processors.Kinect())
    manager.mainloop()
    