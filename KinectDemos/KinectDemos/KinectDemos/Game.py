"""full game built using PyKinect and PyGame"""

from pykinect import nui
from pykinect.nui import JointId, SkeletonTrackingState
import time
import thread
import random

skeleton_to_depth_image = nui.SkeletonEngine.skeleton_to_depth_image
_FLT_EPSILON     = 1.192092896e-07

def skeleton_to_color_image(vPoint, scaleX = 1, scaleY = 1):
    """Given a Vector4 returns X and Y coordinates fo display on the screen.  Returns a tuple depthX, depthY"""

    if vPoint.z > _FLT_EPSILON: 
        ##
        ## Center of depth sensor is at (0,0,0) in skeleton space, and
        ## and (160,120) in depth image coordinates.  Note that positive Y
        ## is up in skeleton space and down in image coordinates.
        ##
        pfDepthX = 0.5 + vPoint.x * ( 531.15   / vPoint.z ) / 640.0
        pfDepthY = 0.5 - vPoint.y * ( 531.15   / vPoint.z ) / 480.0
       
        return pfDepthX * scaleX, pfDepthY * scaleY

    return 0.0, 0.0

import pygame
from pygame.color import THECOLORS
from pygame.locals import *
from pygame import sprite
import ctypes
import math


KINECTEVENT = pygame.USEREVENT
TIMER_EVENT = pygame.USEREVENT + 1

def post_frame(frame):
    """Get skeleton events from the Kinect device and post them into the PyGame event queue"""
    try:
        pygame.event.post(pygame.event.Event(KINECTEVENT, skeletons = frame.SkeletonData))
    except:
        # event queue full
        pass


class NotABall(sprite.Sprite):
    def hit_by_ball(self, cur_ball):
        pass


class BoardPiece(NotABall):
    def __init__(self, x = 50, y = 50, width = 50, height = 50):
        super(BoardPiece, self).__init__()
        
        self.size = pygame.Rect(0, 0, width, height)
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.SurfaceType((width, height))
        self.color = 'white'
        pygame.draw.rect(self.image, THECOLORS['white'], self.size)

    def hit_by_ball(self, cur_ball):
        if cur_ball.color != 'white':
            if cur_ball.color == self.color:
                self.kill()
                cur_ball.player.score += 10
            else:
                pygame.draw.rect(self.image, THECOLORS[cur_ball.color], 
                                 self.size)
                self.color = cur_ball.color
                cur_ball.player.score += 1


class Ball(sprite.Sprite):
    def __init__(self, game, color = 'red', velocity = 8, size = 24, 
                 direction = math.atan2(1, .5), x = 0, y = 0):
        super(Ball, self).__init__()

        self.game = game
        self.size = size
        self.color = color
        self.image = pygame.SurfaceType((size, size))
        self.set_color(color)

        self.velocity = velocity
        self.player = None
        self.direction = direction
        self.old_pos = None        
        self.rect = pygame.Rect(x, y, size, size)

    def set_player(self, new_player):
        self.set_color(new_player.color)
        self.player = new_player

    def set_color(self, new_color):
        self.color = new_color
        pygame.draw.circle(self.image, THECOLORS[new_color], 
                           (self.size/2, self.size/2), self.size/2)

    def update(self, *args):
        r = self.rect
        assert isinstance(r, pygame.Rect)        

        x = r.x + self.velocity * math.cos(self.direction)
        y = r.y + self.velocity * math.sin(self.direction)  
        
        # see if we collide with the walls and reverse directions if necessary        
        if x >= (self.game.width - (self.size)) or x <= 0:
            if y >= (self.game.height - (self.size)) or y <= 0:
                self.direction = math.atan2(math.sin(self.direction) * -1, 
                                            math.cos(self.direction) * -1)
                x = min(max(self.size, x), self.game.width - self.size)
                y = min(max(self.size, y), self.game.height - self.size)
            else:
                self.flip_direction(True)
                x = min(max(self.size, x), self.game.width - self.size)
        elif y >= (self.game.height - (self.size)) or y <= 0:
            self.flip_direction(False)
            y = min(max(self.size, y), self.game.height - self.size)

        self.prev_rect = self.rect
        self.rect = pygame.Rect(int(x), int(y), self.size, self.size)
        return super(Ball, self).update(*args)

    def flip_direction(self, horizontal = True):
        if horizontal:
            self.direction = math.atan2(math.sin(self.direction), 
                                        math.cos(self.direction) * -1)
        else:
            self.direction = math.atan2(math.sin(self.direction) * -1, 
                                        math.cos(self.direction))

    def bounce_ball(self, hit_rect):
        clip = hit_rect.clip(self.rect)
        assert isinstance(clip, pygame.Rect)
    
        # figure out if we need to move more in the X or Y direction to fix our position so we
        # don't overlap
        vel = self.velocity
        x_dist_traveled = clip.width / (math.cos(self.direction) * vel)
        y_dist_traveled = clip.height / (math.sin(self.direction) * vel)
    
        if abs(x_dist_traveled) < abs(y_dist_traveled):
            # we need to backup more in the X direction
            time_adj = x_dist_traveled
        else:
            # we need to backup more in the Y direction
            time_adj = y_dist_traveled 
        
        if clip.left == hit_rect.left:
            self.rect.x -= math.cos(self.direction) * self.velocity * time_adj
        else:
            self.rect.x += math.cos(self.direction) * self.velocity * time_adj

        if clip.top == hit_rect.top:
            self.rect.y -= math.sin(self.direction) * self.velocity * time_adj
        else:
            self.rect.y += math.sin(self.direction) * self.velocity * time_adj
    
        self.flip_direction(clip.width < clip.height)

    def __repr__(self):
        return '<Ball %x>' % id(self)


class Bumper(pygame.sprite.DirtySprite, NotABall):
    """Implements the bumper which the user can move left/right or up/down 
with there hands"""
    def __init__(self, image):
        super(Bumper, self).__init__()

        self.image = image
        self.dirty = 2
        self.rect = self.source_rect = pygame.Rect(0, 0, image.get_width(), 
                                                   image.get_height())

    def hit_by_ball(self, cur_ball):
        cur_ball.set_player(self.player)

class PlayerBackground(pygame.sprite.DirtySprite):
    def __init__(self, player, x, y, width, height):
        super(PlayerBackground, self).__init__()

        self.player = player
        self.image = pygame.SurfaceType((width, height))
        self.image.fill(THECOLORS["white"])
        self.dirty = 2
        self.rect = pygame.Rect(x, y, width, height)
        self.source_rect = pygame.Rect(0, 0, width, height)


class PlayerFace(pygame.sprite.DirtySprite, NotABall):
    def __init__(self, player, x, y, width, height):
        super(PlayerFace, self).__init__()
        
        self.background = PlayerBackground(player, x, y, width, height)

        self.image = player.game.video_screen
        self.dirty = 2
        self.blendmode = BLEND_RGBA_MIN
        self.rect = pygame.Rect(x, y, width, height)
        self.player = player

    def hit_by_ball(self, cur_ball):
        if cur_ball.color != self.player.color:
            cur_ball.player.score += 100
            self.background.image.fill(THECOLORS[cur_ball.color])   
        else:
            cur_ball.player.score += 10
            self.background.image.fill(THECOLORS['white'])


class Player(object):
    def __init__(self, game, color = 'red'):
        self.game = game
        self.left_hand = 0, 0
        self.right_hand = 0, 0
        self.min_left_hand_y = self.game.height / 2 - 1
        self.max_left_hand_y = self.game.height / 2
        self.min_right_hand_y = self.game.height / 2 - 1
        self.max_right_hand_y = self.game.height / 2
        self.active = False
        self.old_rects = [None, None, None, None]        
        self.color = color
        self.score = 0

        self.image1 = pygame.SurfaceType((15, 40))        
        pygame.draw.rect(self.image1, THECOLORS[color], 
                         pygame.Rect(0, 0, 15, 40))

        self.image2 = pygame.SurfaceType((15, 40))
        pygame.draw.rect(self.image2, THECOLORS[color], 
                         pygame.Rect(0, 0, 15, 40))

        self.bumpers = Bumper(self.image1), Bumper(self.image2)
        for bumper in self.bumpers:
            bumper.player = self

        if self.color == 'red':
            x = self.game.blocks_across / 2 - 2
        else: 
            x = self.game.blocks_across / 2

        y = self.game.blocks_down / 2 - 1
        width = (((self.game.width - self.game.left_margin) / 
                  self.game.blocks_across) - 5) * 2
        height = (((self.game.height  - self.game.top_margin) / 
                   self.game.blocks_down) - 5) * 2

        x_loc = ((self.game.width - self.game.left_margin) / 
                 self.game.blocks_across) * x + (self.game.left_margin / 2)
        y_loc = ((self.game.height - self.game.top_margin) / 
                 self.game.blocks_down) * y + (self.game.top_margin / 2)

        self.face = PlayerFace(self, x_loc, y_loc, width, height)

        self.face.player = self
        self.group = sprite.LayeredDirty(self.face.background, self.face, 
                                         *self.bumpers)
    
    def update(self, left, right, head_pos, head_depth):
        self.left_hand = left
        self.right_hand = right
        self.min_left_hand_y = min(self.left_hand[1], self.min_left_hand_y)        
        self.min_right_hand_y = min(self.right_hand[1], self.min_right_hand_y)        
        self.max_left_hand_y = max(self.left_hand[1], self.max_left_hand_y)        
        self.max_right_hand_y = max(self.right_hand[1], self.max_right_hand_y)
        
        pos = self.left_vpos * self.game.height
        self.bumpers[0].rect = pygame.rect.Rect(10, max(pos-10, 0), 15, 40)

        pos = self.right_vpos * self.game.height
        self.bumpers[1].rect = pygame.rect.Rect(self.game.width - 25, 
                                                max(pos-10, 0), 15, 40)

        width = (((self.game.width - self.game.left_margin) / 
                  self.game.blocks_across) - 5) * 2
        height = (((self.game.height - self.game.top_margin) / 
                   self.game.blocks_down) - 5) * 2

        self.face.source_rect = pygame.rect.Rect(head_pos[0]- width / 2, 
                                                 head_pos[1] - height / 2, 
                                                 width, 
                                                 height)

    def draw(self, screen, background):
        self.group.clear(screen, background)
        if self.active:
            with self.game.screen_lock:
                self.group.draw(screen)

    @property
    def left_vpos(self):
        if self.max_left_hand_y == self.min_left_hand_y:
            return 0
        return ((self.left_hand[1] - self.min_left_hand_y) / 
                (self.max_left_hand_y - self.min_left_hand_y))

    @property
    def right_vpos(self):
        if self.max_right_hand_y == self.min_right_hand_y:
            return 0
        return ((self.right_hand[1] - self.min_right_hand_y) / 
                (self.max_right_hand_y - self.min_right_hand_y))


def ball_intersects(left, right):
    """checks if 2 balls intersect by comparing their centers and radius"""
    return ball_distance(left, right) <= 0


def ball_distance(left, right):
    """returns the distance between the radius of two balls"""
    lr = left.size/2    
    lx = left.rect.x + lr
    ly = left.rect.y + lr
    
    rr = right.size/2
    rx = right.rect.x + rr
    ry = right.rect.y + rr

    return (((lx - rx) ** 2) + ((ly - ry) ** 2)) - (lr + rr) ** 2


def dot_product(x, y):
    # computes the dot product of a vector of length 2 stored in a tuple
    return x[0] * y[0] + x[1] * y[1]


def collide_balls(cur_ball, collision):
    # First make sure the balls don't overlap
    dist = ball_distance(cur_ball, collision)
    if dist != 0:
        dist = math.sqrt(abs(dist))
        # there's some overlap, fix the balls...
        angle = math.atan2((cur_ball.rect.y + cur_ball.size/2) - 
                           (collision.rect.y + (collision.rect.height / 2)), 
                           (cur_ball.rect.x + cur_ball.size/2) - 
                           (collision.rect.x + (collision.rect.height / 2)))
        # move back from the normalized angle
        cur_ball.rect.x += .5 * math.cos(angle) * dist
        cur_ball.rect.y += .5 * math.sin(angle) * dist
        collision.rect.x -= .5 * math.cos(angle) * dist
        collision.rect.y -= .5 * math.sin(angle) * dist
    
    # Figure out the new direction for each of the balls...
    # http://www.vobarian.com/collisions/2dcollisions2.pdf
    # Step 1
    n = ((cur_ball.rect.y + cur_ball.size/2) - (collision.rect.y + 
                                                (collision.rect.height / 2)), 
        (cur_ball.rect.x + cur_ball.size/2) - (collision.rect.x + 
                                               (collision.rect.height / 2)))
        
    n_mag = math.sqrt(n[0] ** 2 + n[1] ** 2)
    un = n[0] / n_mag, n[1] / n_mag
    ut = -un[1], un[0]
    
    # Step 2
    v1 = (math.cos(cur_ball.direction) * cur_ball.velocity, 
          math.sin(cur_ball.direction) * cur_ball.velocity)
    v2 = (math.cos(collision.direction) * collision.velocity, 
          math.sin(collision.direction) * collision.velocity)
    
    # Step 3
    v1n = dot_product(un, v1)
    v1t = dot_product(ut, v1)
    v2n = dot_product(un, v2)
    v2t = dot_product(ut, v2)
    
    # Step 4 and 5 omitted (always same mass, just aliasing variables)
    
    # Step 6
    vp1n = v2n * un[0], v2n * un[1]
    vp1t = v1t * ut[0], v1t * ut[1]
    vp2n = v1n * un[0], v1n * un[1]
    vp2t = v2t * ut[0], v2t * ut[1]
    
    # Step 7
    v1p = vp1n[0] + vp1t[0], vp1n[1] + vp1t[1]
    v2p = vp2n[0] + vp2t[0], vp2n[1] + vp2t[1]
    
    v1a = math.atan2(v1p[1], v1p[0])
    v2a = math.atan2(v2p[1], v2p[0])
    
    cur_ball.direction = v2a
    collision.direction = v1a


clock = pygame.time.Clock() 
if hasattr(ctypes.pythonapi, 'Py_InitModule4'):
   Py_ssize_t = ctypes.c_int
elif hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
   Py_ssize_t = ctypes.c_int64
else:
   raise TypeError("Cannot determine type of Py_ssize_t")
_PyObject_AsWriteBuffer = ctypes.pythonapi.PyObject_AsWriteBuffer
_PyObject_AsWriteBuffer.restype = ctypes.c_int
_PyObject_AsWriteBuffer.argtypes = [ctypes.py_object,
                                  ctypes.POINTER(ctypes.c_void_p),
                                  ctypes.POINTER(Py_ssize_t)]

def surface_to_array(surface):
   buffer_interface = surface.get_buffer()
   address = ctypes.c_void_p()
   size = Py_ssize_t()
   _PyObject_AsWriteBuffer(buffer_interface,
                          ctypes.byref(address), ctypes.byref(size))
   bytes = (ctypes.c_byte * size.value).from_address(address.value)
   bytes.object = buffer_interface
   return bytes


class Game(object):
    def __init__(self):
        self.width = 640
        self.height = 480
        pygame.time.set_timer(TIMER_EVENT, 25)
        self.screen_lock = thread.allocate()
        self.last_kinect_event = time.clock()
        self.screen = pygame.display.set_mode((self.width, self.height), 
                                              0, 32)

        self.dispInfo = pygame.display.Info()
        self.screen.convert()
        pygame.display.set_caption('Python Kinect Game')
        self.screen.fill(THECOLORS["black"])
    
        self.background = pygame.Surface((self.width, self.height), 0, 32)
        self.background.fill(THECOLORS["black"])
        self.background.convert()

        self.video_screen = pygame.SurfaceType((self.width, self.height),
                                               0,
                                               32)    

        self.ball_group = sprite.Group(
            Ball(self, 'white', direction = math.atan2(.5, 1), 
                 x = 30, y = 410), 
            Ball(self, 'white', direction = math.atan2(0, -1), 
                 x = 600, y = 400),
            Ball(self, 'white', direction = math.atan2(0, -1), 
                 x = 30, y = 240),
            Ball(self, 'white', direction = math.atan2(1, -1.1), 
                 x = 10, y = 140),
        )
        self.known_players = {}

        self.score_font = pygame.font.SysFont('Segoe UI', 20, bold=True)

        self.pieces_group = sprite.Group()
        
        self.left_margin = (self.width / 5)
        self.top_margin = (self.height / 5)
        self.blocks_across = 10
        self.blocks_down = 10
        width = ((self.width - self.left_margin) / self.blocks_across) - 5
        height = ((self.height - self.top_margin) / self.blocks_down) - 5
        for y in xrange(self.blocks_down):
            for x in xrange(self.blocks_across):
                if x not in (3, 4, 5, 6) or not y in (4, 5):
                    x_loc = ((self.width - self.left_margin) / 
                             self.blocks_across) * x + (self.left_margin / 2)
                    y_loc = ((self.height - self.top_margin) / 
                             self.blocks_down) * y + (self.top_margin / 2)

                    bp = BoardPiece(x_loc, y_loc, width, height)
                    bp.add(self.pieces_group)

        self.bumper_group = sprite.Group()

        self.kinect = nui.Runtime()
        self.kinect.skeleton_engine.enabled = True
        self.kinect.skeleton_frame_ready += post_frame
        self.kinect.video_frame_ready += self.video_frame_ready    
        self.kinect.video_stream.open(nui.ImageStreamType.Video, 2, 
                                      nui.ImageResolution.Resolution640x480, 
                                      nui.ImageType.Color)

    def display_winner(self):
        red_score = 0
        blue_score = 0
        for player in self.known_players.values():
            if player.active:
                if player.color == 'red':
                    red_score = player.score
                else:
                    blue_score = player.score
        
        if red_score == blue_score:
            winner_text = 'Tie Game!'
            winner_color = 'white'
        elif red_score > blue_score:
            winner_text = 'Red Wins!'
            winner_color = 'red'
        else:
            winner_text = 'Blue Wins! '
            winner_color = 'blue'
        
        label = self.score_font.render(winner_text, 
                                       1, 
                                       THECOLORS[winner_color])
        
        assert isinstance(label, pygame.SurfaceType)
        pygame.draw.rect(self.screen, 
                         THECOLORS['black'], 
                         ((self.width - label.get_width()) / 2, 
                          (self.height - label.get_height()) / 2, 
                          label.get_width(), label.get_height()))
        self.screen.blit(label, 
                    ((self.width - label.get_width()) / 2, 
                     (self.height - label.get_height()) / 2))

    def update_score(self):
        for player in self.known_players.values():
            if player.active:
                if player.color == 'red':
                    label = self.score_font.render("Red Score: " + 
                                                   str(player.score), 
                                                   1, THECOLORS["red"])
                    assert isinstance(label, pygame.SurfaceType)
                    pygame.draw.rect(self.screen, THECOLORS['black'], 
                                     (10, 
                                      self.height - label.get_height() - 4,
                                      label.get_width(), label.get_height()))
                    self.screen.blit(label, 
                                     (10, 
                                      self.height - label.get_height() - 4
                                     )
                                    )
                else:
                    label = self.score_font.render("Blue Score: " + 
                                                   str(player.score), 1, 
                                                   THECOLORS["blue"])
                    pygame.draw.rect(self.screen, THECOLORS['black'], 
                                     (self.width - 100, 
                                      self.height - label.get_height() - 4, 
                                      label.get_width(), label.get_height()))
                    self.screen.blit(label, 
                                     (self.width - (label.get_width() + 10), 
                                      self.height - label.get_height() - 4))

    def check_board_piece_collisions(self, cur_ball):
        collisions = pygame.sprite.spritecollide(cur_ball, self.pieces_group, 
                                                 False)
        hit = None
        
        for collision in collisions:
            if hit is None:
                hit = collision.rect
            else:
                hit = collision.rect.union(hit)
        
            collision.hit_by_ball(cur_ball) 
        
        if hit is not None:
            cur_ball.bounce_ball(hit)

    def check_player_collisions(self, cur_ball):
        """checks to see if the ball collides with any of the players"""
        for cur_player in self.known_players.values():
            if cur_player.active:
                collisions = pygame.sprite.spritecollide(cur_ball, 
                                                         cur_player.group, 
                                                         False)
                if collisions:
                    # If we collide with multiple players one wins randomly.
                    collision = collisions[random.randint(0, 
                                                          len(collisions) - 1)]
        
                    if isinstance(collision, NotABall):
                        cur_ball.bounce_ball(collision.rect)
                        collision.hit_by_ball(cur_ball)

    def check_ball_collisions(self, cur_ball):
        """checks to see if a ball collides with any of the other balls on the screen"""
        flipped_balls = set()
        ball_collisions = pygame.sprite.spritecollide(cur_ball, 
                                                      self.ball_group, 
                                                      False, ball_intersects)
        for collision in ball_collisions:
            if collision is not cur_ball and cur_ball not in flipped_balls:
                collide_balls(cur_ball, collision)
                        
                flipped_balls.add(cur_ball)
                flipped_balls.add(collision)
        
    def draw(self):
        """renders the entire frame"""
        for cur_player in self.known_players.values():
            cur_player.draw(self.screen, self.background)
        
        self.pieces_group.clear(self.screen, self.background)
        self.pieces_group.draw(self.screen)
        
        self.ball_group.clear(self.screen, self.background)
        self.ball_group.draw(self.screen)
        
        # update score
        self.update_score()

    def do_update(self):
        """updates the positions of various pieces, and then renders the 
scene"""
        if time.clock() - self.last_kinect_event > 1:
            # haven't seen any players for a second, invalidate them all...
            for player in self.known_players.values():
                player.active = False

        # update the title bar with our frames per second
        pygame.display.set_caption('Python Kinect Game %d fps' % 
                                   clock.get_fps())
        
        # move the balls
        self.ball_group.update()                
        
        for cur_ball in self.ball_group:
            assert isinstance(cur_ball, Ball)
            
            self.check_board_piece_collisions(cur_ball)        
            self.check_player_collisions(cur_ball)
            self.check_ball_collisions(cur_ball)
        
        # draw
        self.draw()

    def process_kinect_event(self, e):
        # first clear all of the active players
        self.last_kinect_event = time.clock()
        for old_player in self.known_players.values():
            old_player.active = False
        
        # then update the players we know based upon if the skeletons are 
        # still tracked
        for skeleton in e.skeletons:         
            if skeleton.eTrackingState == SkeletonTrackingState.TRACKED:
                player = self.known_players.get(skeleton.dwTrackingID)
                if player is not None:
                    player.active = True
        
        for skeleton in e.skeletons:         
            if skeleton.eTrackingState == SkeletonTrackingState.TRACKED:
                player = self.known_players.get(skeleton.dwTrackingID)
                if player is None:
                    # we found a new player, figure out their color.
                    # TODO: We should do something to try and see if any 
                    # of the existing players are actually this player. 
                    # http://social.msdn.microsoft.com/Forums/is/kinectsdk/thread/b0ef83e1-970a-4c80-bc8f-02af218a0568

                    color = 'red'
                    for existing_player in self.known_players.values():
                        if existing_player.active:
                            if existing_player.color == 'red':
                                color = 'blue'
                            break
        
                    player = Player(self, color)
                    self.known_players[skeleton.dwTrackingID] = player
                
                left_hand = skeleton.SkeletonPositions[JointId.HandLeft]
                left_pos = skeleton_to_depth_image(left_hand, 
                                                   self.dispInfo.current_w, 
                                                   self.dispInfo.current_h)
                left_hand = skeleton.SkeletonPositions[JointId.HandRight]
                right_pos = skeleton_to_depth_image(left_hand, 
                                                    self.dispInfo.current_w, 
                                                    self.dispInfo.current_h)
                head = skeleton.SkeletonPositions[JointId.Head]
                head_pos = skeleton_to_color_image(head, 
                                                   self.dispInfo.current_w, 
                                                   self.dispInfo.current_h)
        
                player.update(left_pos, right_pos, head_pos, head.z)

    def play(self):
        # Main game loop    
        while True:
            e = pygame.event.wait()

            if e.type == pygame.QUIT:
                break
            elif e.type == pygame.KEYUP:
                if e.key == K_SPACE and len(self.pieces_group) == 0:
                    # TODO: Start a new game!
                    print 'new game'
                    pass
            elif e.type == KINECTEVENT:
                # process e.skeletons here
                if len(self.pieces_group):
                    self.process_kinect_event(e)
            elif e.type == TIMER_EVENT:
                if not len(self.pieces_group):
                    # game is over
                    self.display_winner()
                else:
                    self.do_update()
                
                pygame.display.flip()
                # maintain 30 fps
                clock.tick(40)
     
    def video_frame_ready(self, frame):
        with self.screen_lock:
            address = surface_to_array(self.video_screen)
            frame.image.copy_bits(address)
            del address


if __name__ == '__main__':
    # Initialize PyGame
    pygame.init()
    pygame.font.init()

    game = Game()
    game.play()
