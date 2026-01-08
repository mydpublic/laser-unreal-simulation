import cv2
import numpy as np


def order_points(points):
    x_sorted = points[np.argsort(points[:, 0]), :]
    left_most, right_most = x_sorted[:2, :], x_sorted[2:, :]

    (tl, bl) = left_most[np.argsort(left_most[:, 1]), :]
    (tr, br) = right_most[np.argsort(right_most[:, 1]), :]

    return np.array([tl, tr, br, bl], dtype="float32")


class Perspective:
    def __init__(self, width, height):
        self.__width = width
        self.__height = height

        self.__static_points = np.float32([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]])
        self.__matrix = cv2.getPerspectiveTransform(self.__static_points, self.__static_points)

    def set_matrix(self, points=None):
        if points is None:
            points = self.__static_points
        self.__matrix = cv2.getPerspectiveTransform(order_points(points), self.__static_points)

    def get_wrap(self, frame):
        return cv2.warpPerspective(frame, self.__matrix, (self.__width, self.__height))
