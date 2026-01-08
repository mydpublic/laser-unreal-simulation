from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSlot, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QPainter, QPen, QFont
from PyQt5.QtWidgets import QLabel

from modules.common.constants import LabelCameraConstants


class LabelTarget(QLabel):
    pixmap_change_signal = pyqtSignal(QPixmap)

    def __init__(self, parent, width=1920, height=1080):
        super().__init__(parent=parent)

        self.all_points = []
        self.selected_rows = []

        self.__size = QSize(width, height)
        self.__center = QPoint(width // 2, height // 2)
        self.__target = QPixmap('images/target.png')
        self.__bullet = QPixmap('images/bullet.png')
        self.__temporary = self.__target.scaled(width, height, Qt.KeepAspectRatio)

        self.__scale_width = 1
        self.__scale_height = 1

        self.__setup_ui(self.__size)

        self.all_mode = True
        self.debug_mode = True

    def set_background(self, background_image):
        self.__target = background_image
        self.__temporary = self.__target.scaled(self.__size, Qt.KeepAspectRatio)
        self.update()

    def __setup_ui(self, size):
        font = QtGui.QFont()
        font.setPointSize(16)

        self.setFont(font)
        self.setGeometry(QtCore.QRect(QPoint(0, 0), size))
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.setStyleSheet("color: white; background: rgba(88,88,88,255);")
        self.setAlignment(QtCore.Qt.AlignCenter)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        scale_value = 25
        size = self.__temporary.size()

        if event.angleDelta().y() > 0:
            size = QSize(size.width() + scale_value, size.height() + scale_value) if \
                size.width() + scale_value < self.__target.width() and \
                size.height() + scale_value < self.__target.height() else \
                QSize(self.__size.width(), self.__size.height())
        elif event.angleDelta().y() < 0:
            size = QSize(size.width() - scale_value, size.height() - scale_value) if \
                size.width() - scale_value > self.__target.width() // 2 and \
                size.height() - scale_value > self.__target.height() // 2 else \
                QSize(self.__size.width() // 2, self.__size.height() // 2)

        self.__temporary = self.__target.scaled(size.width(), size.height(), Qt.KeepAspectRatio)
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.LosslessImageRendering)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        painter.drawPixmap(self.__center.x() - self.__temporary.width() // 2,
                           self.__center.y() - self.__temporary.height() // 2,
                           self.__temporary)

        for order, shot in enumerate(self.all_points) if self.all_mode else \
                zip(self.selected_rows, [self.all_points[index] for index in self.selected_rows]):
            pos = QPoint(int(shot[0][0] * self.__scale_width), int(shot[0][1] * self.__scale_height))
            #pos = QPoint(100,100)
            painter.drawPixmap(QRect(QPoint(int(pos.x() - LabelCameraConstants.SIZE_BULLET_HOLE.width() / 2),
                                            int(pos.y() - LabelCameraConstants.SIZE_BULLET_HOLE.height() / 2)),
                                     LabelCameraConstants.SIZE_BULLET_HOLE), self.__bullet)
            if self.debug_mode:
                painter.setPen(QPen(QtGui.QColor(240, 240, 160, 240), 4))
                painter.setFont(QFont('Consolas', 24))

                painter.drawEllipse(pos,
                                    LabelCameraConstants.SIZE_BULLET_HOLE.width() / 2,
                                    LabelCameraConstants.SIZE_BULLET_HOLE.height() / 2)
                painter.drawText(QPoint(int(pos.x() + LabelCameraConstants.SIZE_BULLET_HOLE.width() / 2),
                                        int(pos.y() - LabelCameraConstants.SIZE_BULLET_HOLE.height() / 2)),
                                 '{}'.format(order + 1))
        painter.end()

    @pyqtSlot(dict)
    def init(self, size):
        self.__scale_width = self.width() / size['width']
        self.__scale_height = self.height() / size['height']

    def update(self) -> None:
        super(LabelTarget, self).update()
        self.pixmap_change_signal.emit(self.grab())
