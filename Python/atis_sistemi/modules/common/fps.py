import time


class FPS:
    def __init__(self):
        self.begin = 0
        self.fps1sec = 0
        self.average_fps = 0

    def calc_fps(self):
        if time.time() - self.begin > 1:
            self.begin = time.time()
            self.average_fps = 0.7 * self.average_fps + 0.3 * self.fps1sec
            self.fps1sec = 0
        self.fps1sec += 1
        return self.average_fps
