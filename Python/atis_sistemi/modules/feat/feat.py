import PyQt5
from PyQt5 import Qt
from PyQt5.QtCore import QPoint, Qt


class Feat:
    def __init__(self, width, height):
        self.__width = width
        self.__height = height

        self.__static_points = PyQt5.Qt.QPolygon([QPoint(0, 0),
                                                  QPoint(width - 1, 0),
                                                  QPoint(width - 1, height - 1),
                                                  QPoint(0, height - 1)])

    def set_feat(self, points):
        self.__static_points = PyQt5.Qt.QPolygon(points)

    def is_in(self, point):
        return self.__static_points.containsPoint(point, Qt.OddEvenFill)
