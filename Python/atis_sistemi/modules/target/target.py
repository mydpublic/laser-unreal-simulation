from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QDesktopWidget

from modules.main.modules.label_target import LabelTarget


class TargetUI(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        self.__setup_ui()
        self.__oldPos = self.pos()

        self.center(1)
        self.show()

    def __setup_ui(self):
        self.resize(1920, 1080)
        self.setMinimumSize(QtCore.QSize(1920, 1080))
        self.setMaximumSize(QtCore.QSize(1920, 1080))
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        self.label_target = LabelTarget(self)
        self.__re_translate_ui()

    def __re_translate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()

    def center(self, screen):
        frame_geo = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry(screen).center()
        frame_geo.moveCenter(center_point)
        self.move(frame_geo.topLeft())

    def mousePressEvent(self, event):
        self.__oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.__oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.__oldPos = event.globalPos()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.center(1) if 0 <= event.globalPos().x() <= self.width() else self.center(0)
