from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QPoint, QSize
from PyQt5.QtWidgets import QLabel


class LabelController(QLabel):

    def __init__(self, parent, label):
        super().__init__(parent=parent)

        self.__label = label
        self.__setup_ui()

    def __setup_ui(self):
        font = QtGui.QFont()
        font.setPointSize(16)
        size = QSize(960, 540)

        self.setFont(font)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet("color: white; background: black;")
        self.setGeometry(QtCore.QRect(QPoint(0, 0), size))
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.setScaledContents(True)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        self.__label.wheelEvent(event)
