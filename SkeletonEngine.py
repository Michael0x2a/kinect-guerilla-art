from pykinect import nui
with nui.Runtime() as kinect:
    kinect.skeleton_engine.enabled = True
    while True:
        frame = kinect.skeleton_engine.get_next_frame()
        for skeleton in frame.SkeletonData:
            if skeleton.eTrackingState == nui.SkeletonTrackingState.TRACKED:
                print skeleton
