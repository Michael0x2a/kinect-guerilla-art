#!/usr/bin/env python

import pygame

import pykinect
from pykinect import nui

class Mouse(object):
    def __init__(self):
        pygame.init()
        self.previous = None
        self.previous_time = 0
        
    def get_pos(self):
        '''Returns a list of mouse positions (for when there are multiple
        mouses)'''
        # in screen pixels
        x, y = pygame.mouse.get_pos()
        # assuming in meters.
        z = 2.0
        location = [(x, y, z)]
        if pygame.time.get_ticks() - 100 > self.previous_time:
            self.previous_time = pygame.time.get_ticks()
            self.previous = location
        return location
        
    def motion_detected(self):
        return self.previous != self.get_pos()
        
    def ignore(self, id):
        pass
        
        
class Kinect(object):
    def __init__(self, size=(1600, 900)):
        pygame.init()
        self.kinect = nui.Runtime()
        self.kinect.skeleton_engine.enabled = True
        
        self.screen_width, self.screen_height = size
        
        self.people = []
        self.ignore_list = []
        
    def _update(self):
        self.people = []
        frame = self.kinect.skeleton_engine.get_next_frame()
        for person in frame.SkeletonData:
            if person.eTrackingState == nui.SkeletonTrackingState.TRACKED:
                self.people.append(person)
        return self.people
                
                
    def get_pos(self):
        self._update()
        last_pos = []
        for person in self.people:
            pos1 = nui.SkeletonEngine.skeleton_to_depth_image(
                person.SkeletonPositions[nui.JointId.HandLeft], 
                self.screen_width,
                self.screen_height
            )
            pos1 = list(pos1)
            pos1.append(person.SkeletonPositions[nui.JointId.HandLeft].z)
            
            pos2 = nui.SkeletonEngine.skeleton_to_depth_image(
                person.SkeletonPositions[nui.JointId.HandRight], 
                self.screen_width,
                self.screen_height
            )
            pos2 = list(pos2)
            pos2.append(person.SkeletonPositions[nui.JointId.HandRight].z)
            
            last_pos.append(pos1)
            last_pos.append(pos2)
        return last_pos
        
    def motion_detected(self):
        self._update()
        return len(self.people) > 0
            
    def ignore(self, id):
        self.ignore_list.append(id)
        
    def too_close(self):
        self._update()
        for person in self.people:
            z = person.SkeletonPositions[nui.JointId.Spine].z
            if z <= 1.5:
                return True
                
