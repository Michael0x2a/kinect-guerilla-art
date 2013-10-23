from pykinect import nui

with nui.Runtime() as kinect:
    dir = 2
    while True:
        new_angle = kinect.camera.elevation_angle + dir
        if new_angle > kinect.camera.ElevationMaximum:
            dir *= -1
        else:
            print new_angle
            kinect.camera.elevation_angle = new_angle

