from PyQt5 import QtWidgets
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTableWidget

from modules.common.constants import MainUIConstants, TableShotsConstants


class TableShots(QTableWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.__setup_ui()

    def __setup_ui(self):
        font = QFont()
        font.setPointSize(MainUIConstants.FONT_SIZE_DEFAULT)

        self.setGeometry(QRect(TableShotsConstants.INIT_POINT_TABLE_SHOTS, TableShotsConstants.SIZE_TABLE_SHOTS))
        self.setFont(font)
        self.setColumnCount(2)
        # self.setColumnCount(4)
        # self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('X'))
        # self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Y'))
        self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Time'))
        self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Success'))
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def clear(self) -> None:
        super().clear()

        self.setRowCount(0)
        # self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('X'))
        # self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Y'))
        self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Time'))
        self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Success'))
