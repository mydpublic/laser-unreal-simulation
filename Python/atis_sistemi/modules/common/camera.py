import multiprocessing
import time
from collections import deque
from datetime import datetime
from multiprocessing.pool import ThreadPool

import cv2
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

from modules.common.constants import CameraConstants
from modules.common.detection import Detection
from modules.common.fps import FPS
from modules.feat.feat import Feat
from modules.perspective.perspective import Perspective


class CameraWork(QObject):
    finished = pyqtSignal()
    init_signal = pyqtSignal(dict)
    detected_signal = pyqtSignal(list)
    fps_change_signal = pyqtSignal(float)
    pixmap_change_signal = pyqtSignal(np.ndarray)

    def __init__(self, camera_id=CameraConstants.CAMERA_ID, camera_fps=CameraConstants.CAMERA_FPS,
                 camera_width=CameraConstants.CAMERA_WIDTH, camera_height=CameraConstants.CAMERA_HEIGHT):
        super().__init__()

        self.__capture = cv2.VideoCapture(camera_id)

        if not self.__capture.isOpened():
            raise Exception('Camera could not be opened!')

        self.__capture.set(cv2.CAP_PROP_FPS, camera_fps)
        self.__capture.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
        self.__capture.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

        self.available_width = int(self.__capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.available_height = int(self.__capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.feat = Feat(self.available_width, self.available_height)
        self.perspective = Perspective(self.available_width, self.available_height)

        self.__fps = FPS()
        self.__detection = Detection()

        self.isWorkerAlive = True
        self.isCameraRunning = True
        self.isDetectionRunning = False

    def run(self):
        self.init_signal.emit({
            'width': int(self.available_width),
            'height': int(self.available_height)
        })

        cpu_count = multiprocessing.cpu_count()-1
        pool = ThreadPool(processes=cpu_count)
        pending_task = deque()

        begin = time.time()
        delay = CameraConstants.DETECTION_DELAY_MS

        while self.isWorkerAlive:
            while len(pending_task) > 0 and pending_task[0].ready():
                points = pending_task.popleft().get()
                if len(points) > 0 and time.time() - begin > delay:
                    begin = time.time()
                    self.detected_signal.emit([points[0], datetime.now().strftime("%H:%M:%S")])

            if self.isCameraRunning:
                if len(pending_task) < cpu_count:
                    ret, frame = self.__capture.read()
                    self.fps_change_signal.emit(self.__fps.calc_fps())

                    if not ret:
                        # raise Exception('Frame could not be loaded!')
                        self.__capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue

                    wrapped = self.perspective.get_wrap(frame)

                    if self.isDetectionRunning:
                        task = pool.apply_async(self.__detection.detect, (wrapped,))
                        pending_task.append(task)
                    else:
                        self.pixmap_change_signal.emit(wrapped)
        self.__capture.release()
        self.finished.emit()
