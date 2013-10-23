"""simple console app which tracks and draws where the players hands are located"""
from pykinect import nui
from pykinect.nui import JointId, SkeletonTrackingState

skeleton_to_depth_image = nui.SkeletonEngine.skeleton_to_depth_image

import msvcrt
import ctypes

SetConsoleCursorPosition = ctypes.WinDLL('kernel32').SetConsoleCursorPosition
GetStdHandle = ctypes.WinDLL('kernel32').GetStdHandle

class Coord(ctypes.Structure):
    _fields_ = [('X', ctypes.c_int16), ('Y', ctypes.c_int16)]

    def __init__(self, x, y):
        self.X = x
        self.Y = y


SetConsoleCursorPosition.argtypes = [ctypes.c_int32, Coord]
CONSOLE_HANDLE = GetStdHandle(-11) 

def write_char(location, char):
    if location is not None:
        SetConsoleCursorPosition(CONSOLE_HANDLE, location)
        print char,

with nui.Runtime() as kinect:
    kinect.skeleton_engine.enabled = True
    last_l = None
    last_r = None
    while True:
        frame = kinect.skeleton_engine.get_next_frame()
        
        for skeleton in frame.SkeletonData:
            if skeleton.eTrackingState == SkeletonTrackingState.TRACKED:
                coord_l = skeleton_to_depth_image(
                                    skeleton.SkeletonPositions[JointId.HandLeft], 
                                    80, 
                                    25)
                coord_r = skeleton_to_depth_image(
                                    skeleton.SkeletonPositions[JointId.HandRight], 
                                    80, 
                                    25)

                write_char(last_l, ' ')
                write_char(last_r, ' ')
                write_char(Coord(int(coord_l[0]), int(coord_l[1])), 'L')
                write_char(Coord(int(coord_r[0]), int(coord_r[1])), 'R')
