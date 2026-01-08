import cv2
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap


class Statics:
    @staticmethod
    def cv2qt(cv_image, label):
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        convert_to_qt_format = QtGui.QImage(rgb_image.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
        scaled = convert_to_qt_format.scaled(label.width(), label.height())
        return QPixmap.fromImage(scaled)

    @staticmethod
    def available_devices():
        cameras = list()

        for index in range(10):
            capture = cv2.VideoCapture(index)
            if capture.isOpened():
                capture.release()
                cameras.append(index)
        return cameras
