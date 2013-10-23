#!/usr/bin/env python

import pygame
import colorsys

COLORS = {
    'red': (255, 128, 128),
    'blue': (120, 155, 239),
    'green': (109, 209, 105),
    'purple': (205, 102, 192),
    'aqua': (93, 185, 170),
    'orange': (243, 187, 122)
}


def center_text(screen, text_surface, base_y):
    width = text_surface.get_width()
    screen.blit(
        text_surface,
        (800 - int(width / 2), base_y)
    )
    return screen
    
CORNERS = {
    'up_left': pygame.Rect((300, 300), (300, 100)),
    'up_right': pygame.Rect((1600 - 300 - 300, 300), (300, 100)),
    'down_left': pygame.Rect((300, 900 - 100 - 300), (300, 100)),
    'down_right': pygame.Rect((1600 - 300 - 300, 900 - 100 - 300), (300, 100)) 
}
    
def button(screen, text_surface, corner):
    rect = CORNERS[corner]
    pygame.draw.rect(screen, (255, 255, 255), rect, 5)
    mid_width, mid_height = text_surface.get_size()
    mid_width = mid_width / 2
    mid_height = mid_height / 2
    
    screen.blit(
        text_surface,
        (rect.centerx - mid_width, rect.centery - mid_height)
    )
    return screen
    
def progress(screen, corner, progress, max_progress):
    rect = CORNERS[corner]
    if progress > max_progress:
        progress = max_progress
    rect2 = rect.copy()
    rect2.width = int(rect.width * progress / float(max_progress))
    
    pygame.draw.rect(screen, (255, 255, 255), rect2)
    
def is_hover(coord, corner):
    return CORNERS[corner].collidepoint(coord)
        
def generate_text(text, size, color=(255, 255, 255)):
    return pygame.font.Font(None, size).render(text, True, color)
    
def fade_color(rgb, fade):
    h, s, l = colorsys.rgb_to_hsl(*rgb)
    return colorsys.hsl_to_rgb(h, s, fade)
    
    
class Options(object):
    def __init__(self, buttons, input):
        self.buttons = {button: 0 for button in buttons}
        self.input = input
        self.trying = False
        
    def handle(self, screen):
        mapping = {button: False for button in self.buttons}
        for x, y, z in self.input.get_pos():
            for button in mapping:
                if not mapping[button]:
                    mapping[button] = is_hover((x, y), button)
                    if mapping[button]:
                        self.buttons[button] += 1
        
        if sum([1 for button in mapping if mapping[button]]) != 1:
            self.reset()
            self.trying = False
        else:
            self.trying = True
           
        for button in self.buttons:
            progress(screen, button, self.buttons[button], 20)
            if self.buttons[button] > 20:
                return screen, button
                
        return screen, None
        
    def is_trying(self):
        return self.trying
            
    def reset(self):
        for button in self.buttons:
            self.buttons[button] = 0
            

class Lonely(object):
    def __init__(self, input):
        self.input = input
        self.hello = generate_text("Hello? My name is Charlie.", 144)
        self.lonely = generate_text("(I'm lonely.)", 72)
        self.plea = generate_text("Won't you play with me?", 144)
        self.active = True
        
    def loop(self, screen):
        screen = center_text(screen, self.hello, 100)
        screen = center_text(screen, self.lonely, 414)
        screen = center_text(screen, self.plea, 658)
        if self.input.motion_detected():
            return screen, 'Hopeful'
        else:
            return screen, None
        
class Hopeful(object):
    def __init__(self, input):
        self.input = input
        self.active = False
        self.hello = generate_text("Hi!", 144)
        self.plea = generate_text("Do you want to play with me?", 144)
        self.yes = generate_text("Yes", 144)
        self.no = generate_text("No", 144)
        
        self.options = Options(['down_left', 'down_right'], self.input)
        
    def loop(self, screen):
        screen = center_text(screen, self.hello, 100)
        screen = center_text(screen, self.plea, 314)
        
        screen = button(screen, self.no, 'down_left')
        screen = button(screen, self.yes, 'down_right')

        screen, choice = self.options.handle(screen)
        self.active = self.options.is_trying()
        
        if choice == 'down_left':
            return screen, 'Why'
        elif choice == 'down_right':
            return screen, 'Choices'
        
        return screen, None
        
class Why(object):
    def __init__(self, input):
        self.input = input
        self.active = False
        self.why = generate_text("Why?", 150)
        
        self.busy = generate_text("I'm busy", 50)
        self.hate = generate_text("I don't like you", 50)
        self.dont_like_games = generate_text("I don't like games", 50)
        self.back = generate_text("I didn't mean it", 50)
        
        self.options = Options(['down_left', 'down_right', 'up_left', 'up_right'], self.input)
        
        self.ok = generate_text("Oh, ok.", 150)
        self.weird = generate_text("You're weird.", 150)
        
        self.start = 0
        
        self.text = None
        
    def loop(self, screen):
        screen.fill(COLORS['purple'])
        choice = None
        if self.text is None:
            screen = center_text(screen, self.why, 10)
            
            screen = button(screen, self.busy, 'down_left')
            screen = button(screen, self.hate, 'down_right')
            screen = button(screen, self.dont_like_games, 'up_left')
            screen = button(screen, self.back, 'up_right')
            
            screen, choice = self.options.handle(screen)
        else:
            screen = center_text(screen, self.text, int(450 - 150 / 2))
            if pygame.time.get_ticks() - self.start > 5000:
                return screen, 'Sad'
        
        self.active = self.options.is_trying()
        
        if choice == 'down_left':
            self.text = self.ok
            self.start = pygame.time.get_ticks()
        elif choice == 'down_right':
            return screen, 'Sad'
        elif choice == 'up_left':
            self.text = self.weird
            self.start = pygame.time.get_ticks()
        elif choice == 'up_right':
            return screen, 'Choices'
            
        return screen, None
            

class Choices(object):
    def __init__(self, input):
        self.input = input
        self.active = False
        
        self.text = generate_text("What do you want to do?", 144)
        self.joke = generate_text("Tell a joke!", 50)
        self.pong = generate_text("Play ping pong!", 50)
        
        self.options = Options(['down_left', 'down_right'], self.input)
        
    def loop(self, screen):
        screen.fill(COLORS['green'])
        screen = center_text(screen, self.text, 314)
        
        screen = button(screen, self.joke, 'down_left')
        screen = button(screen, self.pong, 'down_right')

        screen, choice = self.options.handle(screen)
        self.active = self.options.is_trying()
        
        if choice == 'down_left':
            return screen, 'Joke'
        elif choice == 'down_right':
            return screen, 'Happy'
        return screen, None
        
class Happy(object):
    def __init__(self, input):
        self.input = input
        self.active = True
        
        self.text = generate_text(":)", 300)
        
        self.start = pygame.time.get_ticks()
        
    def loop(self, screen):
        delta = pygame.time.get_ticks() - self.start
        if delta > 3000:
            return screen, 'Lonely'
            
        screen = center_text(screen, self.text, 300)
            
        return screen, None

        
class Joke(object):
    def __init__(self, input):
        self.input = input
        self.active = True
        
        self.text = generate_text("Ok, you start!", 150)
        self.smile = [
            generate_text(":)", 300),
            generate_text(":|", 300),
            generate_text(":(", 300)
        ]
        self.cannot = generate_text("I can't hear you...", 150)
        
        self.start = pygame.time.get_ticks()
        
    def loop(self, screen):
        delta = pygame.time.get_ticks() - self.start
        if delta > 6000:
            delta = 6000
        screen = center_text(screen, self.text, 100)
        screen = center_text(screen, self.smile[int(delta / 3000)], 300)
        if delta == 6000:
            screen = center_text(screen, self.cannot, 900 - 150 - 100)
            
        if pygame.time.get_ticks() - self.start > 9000:
            return screen, 'Sad'
        
        return screen, None
        

        

        
class Sad(object):
    def __init__(self, input):
        self.active = True
        self.frown = generate_text(":(", 300)
        self.start = pygame.time.get_ticks()
        
    def loop(self, screen):
        screen = center_text(screen, self.frown, 300)
        
        time = pygame.time.get_ticks()
        if time - self.start > 5000:
            return screen, 'Lonely'
        else:
            return screen, None
            
class Scared(object):
    def __init__(self, input, next_interaction):
        self.input = input
        self.active = True
        self.start = pygame.time.get_ticks()
        self.next = next_interaction
        self.cry = generate_text("You're hurting me!", 150)
        self.face = generate_text(":(", 300)
        self.request = generate_text("Could you back away a bit?", 150)
        
    def loop(self, screen):
        if pygame.time.get_ticks() % 500 < 250:
            screen.fill(COLORS['red'])
        else:
            screen.fill(COLORS['orange'])
        
        screen = center_text(screen, self.cry, 100)
        screen = center_text(screen, self.face, 300)
        screen = center_text(screen, self.request, 900 - 150 - 100)
        
        
        if pygame.time.get_ticks() - self.start > 5000:
            return screen, 'Dead'
        if not self.input.too_close():
            return screen, self.next
        
        return screen, None
        
class Dead(object):
    def __init__(self, input):
        self.active = True
        self.start = pygame.time.get_ticks()
        self.dead = generate_text("X_X", 300)
        
    def loop(self, screen):
        screen.fill((0,0,0))
        screen = center_text(screen, self.dead, 300)
        if pygame.time.get_ticks() - self.start > 20000:
            return screen, 'Lonely'
        return screen, None
        
   
INTERACTIONS = {
    'Lonely': Lonely,
    'Hopeful': Hopeful,
    'Sad': Sad,
    'Scared': Scared,
    'Dead': Dead,
    'Why': Why,
    'Joke': Joke,
    'Choices': Choices,
    'Happy': Happy
}
        