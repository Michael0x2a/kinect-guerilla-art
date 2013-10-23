from pykinect import nui
import time

with nui.Runtime() as kinect:
    kinect.skeleton_engine.enabled = True
    def frame_ready(frame):
        print frame

    kinect.skeleton_frame_ready += frame_ready
    time.sleep(10000)
