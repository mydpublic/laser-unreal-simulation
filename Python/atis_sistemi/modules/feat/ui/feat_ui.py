import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QPoint, pyqtSlot
from PyQt5.QtGui import QPolygon, QColor, QPen
from PyQt5.QtWidgets import QMessageBox

from modules.common.statics import Statics


class FeatUI(QtWidgets.QDialog):
    feat_change_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        self.__scale_width = 1
        self.__scale_height = 1

        self.__setup_ui()

    def __setup_ui(self):
        self.resize(960, 600)
        self.setMinimumSize(QtCore.QSize(960, 600))
        self.setMaximumSize(QtCore.QSize(960, 600))

        font = QtGui.QFont()
        font.setPointSize(16)

        self.label_camera = CustomLabel(self)
        self.label_camera.mouse_move.connect(self.__update_mouse)
        self.label_camera.setGeometry(QtCore.QRect(0, 0, 960, 540))
        self.label_camera.setFont(font)
        self.label_camera.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.label_camera.setStyleSheet("color: white; background: black;")
        self.label_camera.setAlignment(QtCore.Qt.AlignCenter)
        self.label_camera.setMouseTracking(True)

        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 550, 941, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_mouse = QtWidgets.QHBoxLayout()

        font.setPointSize(10)
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.label_mouse_text = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label_mouse_text.setFont(font)
        self.horizontalLayout_mouse.addWidget(self.label_mouse_text)
        self.label_mouse = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label_mouse.setFont(font)
        self.horizontalLayout_mouse.addWidget(self.label_mouse)
        self.horizontalLayout.addLayout(self.horizontalLayout_mouse)

        self.horizontalLayout.addItem(spacer_item)

        self.horizontalLayout_buttons = QtWidgets.QHBoxLayout()
        self.button_clear = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.button_clear.setFont(font)
        self.button_clear.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.horizontalLayout_buttons.addWidget(self.button_clear)
        self.button_cancel = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.button_cancel.setFont(font)
        self.button_cancel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.horizontalLayout_buttons.addWidget(self.button_cancel)
        self.button_calibrate = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.button_calibrate.setFont(font)
        self.button_calibrate.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.horizontalLayout_buttons.addWidget(self.button_calibrate)
        self.horizontalLayout.addLayout(self.horizontalLayout_buttons)

        self.button_clear.clicked.connect(self.__clear)
        self.button_cancel.clicked.connect(self.__cancel)
        self.button_calibrate.clicked.connect(self.__calibrate)

        self._re_translate_ui()

    def _re_translate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Feat Calibration"))
        self.label_camera.setText(_translate("Dialog", "Camera Not Found"))
        self.label_mouse_text.setText(_translate("Dialog", "Mouse:"))
        self.label_mouse.setText(_translate("Dialog", "0, 0"))
        self.button_clear.setText(_translate("Dialog", "Clear"))
        self.button_cancel.setText(_translate("Dialog", "Close"))
        self.button_calibrate.setText(_translate("Dialog", "Determine"))

    def __clear(self):
        self.label_camera.points.clear()
        self.button_calibrate.setEnabled(True)

    def __cancel(self):
        self.close()

    def __calibrate(self):
        if len(self.label_camera.points) > 2:
            instant = list()
            for point in self.label_camera.points:
                instant.append(QPoint(int(point.x() / self.__scale_width), int(point.y() / self.__scale_height)))
            self.feat_change_signal.emit(instant)
            self.button_calibrate.setEnabled(False)
        else:
            QMessageBox.about(self, "Warning", "You must select at least three points.")

    @pyqtSlot(QPoint)
    def __update_mouse(self, pos):
        self.label_mouse.setText('{}, {}'.format(pos.x(), pos.y()))

    @pyqtSlot(np.ndarray)
    def update_label(self, cv_img):
        self.label_camera.setPixmap(Statics.cv2qt(cv_img, self.label_camera))

    @pyqtSlot(dict)
    def init(self, size):
        self.__scale_width = self.label_camera.width() / size['width']
        self.__scale_height = self.label_camera.height() / size['height']


class CustomLabel(QtWidgets.QLabel):
    point_add = pyqtSignal(tuple)
    mouse_move = pyqtSignal(QPoint)

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.points = list()

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.points.append(ev.pos())

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)
        painter.setPen(QPen(QColor(80, 160, 240), 2))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(QtGui.QColor(80, 160, 240, 50))))

        painter.drawPolyline(QPolygon(self.points))
        if len(self.points) > 1:
            painter.drawLine(self.points[-1], self.points[0])

        for point in self.points:
            painter.drawEllipse(point, 10, 10)

        painter.end()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.mouse_move.emit(ev.pos())
