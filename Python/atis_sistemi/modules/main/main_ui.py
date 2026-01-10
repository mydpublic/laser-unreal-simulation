import functools
import time

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSlot, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog

from modules.common.camera import CameraWork
from modules.common.constants import MainUIConstants
from modules.common.filer import Filer
from modules.common.statics import Statics
from modules.feat.ui.feat_ui import FeatUI
from modules.main.modules.label_controller import LabelController
from modules.main.modules.table_shots import TableShots
from modules.perspective.ui.perspective_ui import PerspectiveUI
from modules.target.target import TargetUI


class MainUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.__devices = []
        self.__filer = Filer()
        self.__thread = QThread()

        self.__feat_ui = FeatUI()
        self.__target_ui = TargetUI()
        self.__perspective_ui = PerspectiveUI()

        self.__setup_ui()
        self.__re_translate_ui()

        self.show()
        self.__target_ui.show()
        self.__target_ui.label_target.update()

        if len(self.__devices) > 0:
            self.__init_camera(self.__devices[0])
        else:
            QMessageBox.about(self, 'Warning', 'Camera device not found!')

    def __setup_ui(self):
        font = QtGui.QFont()
        font.setPointSize(MainUIConstants.FONT_SIZE_DEFAULT)

        self.resize(MainUIConstants.SCREEN_WIDTH, MainUIConstants.SCREEN_HEIGHT)
        self.setMinimumSize(QtCore.QSize(MainUIConstants.SCREEN_MIN_WIDTH, MainUIConstants.SCREEN_HEIGHT))
        self.setMaximumSize(QtCore.QSize(MainUIConstants.SCREEN_WIDTH, MainUIConstants.SCREEN_HEIGHT))
        self.central_widget = QtWidgets.QWidget(self)

        # Label Camera
        self.label_camera = LabelController(self.central_widget, self.__target_ui.label_target)
        self.__target_ui.label_target.pixmap_change_signal.connect(self.label_camera.setPixmap)
        # Table Shots
        self.table_shots = TableShots(self.central_widget)

        # Buttons
        self.gridLayoutWidget = QtWidgets.QWidget(self.central_widget)
        self.gridLayoutWidget.setGeometry(
            QtCore.QRect(MainUIConstants.INIT_POINT_GRID_BUTTONS, MainUIConstants.SIZE_GRID_BUTTONS))
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(MainUIConstants.SPACING_GRID_LAYOUT)

        # Button Show Selected
        self.button_show_selected = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.button_show_selected.setFont(font)
        self.button_show_selected.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.gridLayout.addWidget(self.button_show_selected, 0, 0, 1, 1)

        # Button Show All
        self.button_show_all = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.button_show_all.setFont(font)
        self.button_show_all.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.gridLayout.addWidget(self.button_show_all, 0, 1, 1, 1)

        # Button Clear
        self.button_clear = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.button_clear.setFont(font)
        self.button_clear.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.gridLayout.addWidget(self.button_clear, 1, 0, 1, 1)

        # Button Start/Stop
        self.button_start = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.button_start.setFont(font)
        self.button_start.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.gridLayout.addWidget(self.button_start, 1, 1, 1, 1)

        self.setCentralWidget(self.central_widget)

        # Menubar
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(MainUIConstants.INIT_POINT_MENU_BAR, MainUIConstants.SIZE_MENU_BAR))
        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_operations = QtWidgets.QMenu(self.menubar)
        self.menu_camera_devices = QtWidgets.QMenu(self.menu_operations)
        self.setMenuBar(self.menubar)

        self.__devices = Statics.available_devices()
        for index in self.__devices:
            self.menu_camera_devices.addAction('Camera {}'.format(index),
                                               functools.partial(self.__change_camera, index))

        self.action_camera_calibration = QtWidgets.QAction(self)
        self.action_target_area = QtWidgets.QAction(self)
        self.action_change_background = QtWidgets.QAction(self)
        self.action_debug = QtWidgets.QAction(self)
        self.action_save = QtWidgets.QAction(self)
        self.action_load = QtWidgets.QAction(self)
        self.action_exit = QtWidgets.QAction(self)

        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_load)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)

        self.menu_operations.addAction(self.action_camera_calibration)
        self.menu_operations.addAction(self.menu_camera_devices.menuAction())
        self.menu_operations.addAction(self.action_change_background)
        self.menu_operations.addAction(self.action_debug)
        self.menu_operations.addAction(self.action_target_area)

        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_operations.menuAction())

        # Status bar
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        # Button Connections
        self.button_show_selected.clicked.connect(self.show_selected)
        self.button_show_all.clicked.connect(self.show_all)
        self.button_clear.clicked.connect(self.clear)
        self.button_start.clicked.connect(self.start)

        # Action Connections
        self.action_camera_calibration.triggered.connect(self.camera_calibration)
        self.action_target_area.triggered.connect(self.target_area)
        self.action_change_background.triggered.connect(self.change_background)
        self.action_debug.triggered.connect(self.debug)
        self.action_save.triggered.connect(self.save)
        self.action_load.triggered.connect(self.load)
        self.action_exit.triggered.connect(self.close)

    def __re_translate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Laser"))
        self.label_camera.setText(_translate("MainWindow", "Camera Not Found"))
        self.button_show_selected.setText(_translate("MainWindow", "Show Selected"))
        self.button_show_all.setText(_translate("MainWindow", "Show All"))
        self.button_clear.setText(_translate("MainWindow", "Clear"))
        self.button_start.setText(_translate("MainWindow", "Start"))
        self.menu_file.setTitle(_translate("MainWindow", "File"))
        self.menu_operations.setTitle(_translate("MainWindow", "Operations"))
        self.action_camera_calibration.setText(_translate("MainWindow", "Camera Calibration"))
        self.action_change_background.setText(_translate("MainWindow", "Change Background"))
        self.action_target_area.setText(_translate("MainWindow", "Target Area"))
        self.action_debug.setText(_translate("MainWindow", "Debug"))
        self.menu_camera_devices.setTitle(_translate("MainWindow", "Camera Devices"))
        self.action_save.setText(_translate("MainWindow", "Save"))
        self.action_load.setText(_translate("MainWindow", "Load"))
        self.action_exit.setText(_translate("MainWindow", "Exit"))

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.__feat_ui.close()
        self.__target_ui.close()
        self.__perspective_ui.close()

        # Check if worker exists before accessing (worker may not be initialized if no camera found)
        if hasattr(self, '_MainUI__worker'):
            self.__worker.isWorkerAlive = False
            self.__worker.isCameraRunning = False
            self.__worker.isDetectionRunning = False

    def __change_camera(self, camera_id):
        if self.__thread.isRunning():
            self.__worker.isWorkerAlive = False
            self.__thread.quit()

            while self.__thread.isRunning():
                time.sleep(0.1)

        self.__init_camera(camera_id)

    def __init_camera(self, camera_id):
        self.__worker = CameraWork(camera_id)
        self.__worker.moveToThread(self.__thread)

        self.__worker.finished.connect(self.__worker.deleteLater)

        self.__worker.init_signal.connect(self.__target_ui.label_target.init)
        self.__worker.init_signal.connect(self.__feat_ui.init)
        self.__worker.init_signal.connect(self.__perspective_ui.init)

        self.__worker.pixmap_change_signal.connect(self.__feat_ui.update_label)
        self.__worker.pixmap_change_signal.connect(self.__perspective_ui.update_label)

        self.__worker.detected_signal.connect(self.bundler)
        self.__worker.fps_change_signal.connect(self.get_statusbar_message)

        self.__feat_ui.feat_change_signal.connect(self.update_feat)
        self.__perspective_ui.perspective_change_signal.connect(self.update_perspective)

        self.__thread.started.connect(self.__worker.run)
        self.__thread.start()

    @pyqtSlot(list)
    def bundler(self, bundle):
        self.__target_ui.label_target.all_points.append(bundle)
        order = len(self.__target_ui.label_target.all_points)
        self.table_shots.setRowCount(order)

        x = QTableWidgetItem(str(bundle[0][0]))
        x.setTextAlignment(Qt.AlignCenter)

        y = QTableWidgetItem(str(bundle[0][1]))
        y.setTextAlignment(Qt.AlignCenter)

        date = QTableWidgetItem(str(bundle[1]))
        date.setTextAlignment(Qt.AlignCenter)

        success = QTableWidgetItem()
        success.setTextAlignment(Qt.AlignCenter)
        success.setBackground(Qt.green if self.__worker.feat.is_in(QPoint(bundle[0][0], bundle[0][1])) else Qt.red)

        # self.table_shots.setItem(order - 1, 0, x)
        # self.table_shots.setItem(order - 1, 1, y)
        self.table_shots.setItem(order - 1, 0, date)
        self.table_shots.setItem(order - 1, 1, success)
        self.table_shots.scrollToBottom()

        self.__target_ui.label_target.update()

    @pyqtSlot(list)
    def update_feat(self, points):
        self.__worker.feat.set_feat(points)

    @pyqtSlot(np.ndarray)
    def update_perspective(self, points):
        self.__worker.perspective.set_matrix(None if len(points) == 0 else points)

    @pyqtSlot(float)
    def get_statusbar_message(self, fps):
        self.statusbar.showMessage('FPS: {:.3f} {} {} {} {}'.format(
            fps,
            '- Camera Running' if self.__worker.isCameraRunning else '- Camera Not Running',
            '- Detection Running' if self.__worker.isDetectionRunning else '- Detection Not Running',
            '- Show All' if self.__target_ui.label_target.all_mode else ' - Show Selected',
            '- Debug' if self.__target_ui.label_target.debug_mode else ''))

    def show_selected(self):
        self.__target_ui.label_target.selected_rows = [index.row() for index in
                                                       self.table_shots.selectionModel().selectedRows()]
        self.__target_ui.label_target.all_mode = False
        self.__target_ui.label_target.update()

    def show_all(self):
        self.__target_ui.label_target.all_mode = True
        self.__target_ui.label_target.update()

    def clear(self):
        self.__target_ui.label_target.all_points.clear()
        self.__target_ui.label_target.selected_rows.clear()
        self.__target_ui.label_target.update()
        self.table_shots.clear()

    def start(self):
        if self.__worker.isDetectionRunning:
            self.button_start.setText('Start')
            self.__worker.isDetectionRunning = False
            self.action_camera_calibration.setEnabled(True)
            self.menu_camera_devices.setEnabled(True)
            self.action_target_area.setEnabled(True)
        else:
            self.button_start.setText('Stop')
            self.__worker.isDetectionRunning = True
            self.action_camera_calibration.setEnabled(False)
            self.menu_camera_devices.setEnabled(False)
            self.action_target_area.setEnabled(False)

            self.__feat_ui.close()
            self.__perspective_ui.close()

    def camera_calibration(self):
        self.__perspective_ui.show()

    def target_area(self):
        self.__feat_ui.show()

    def debug(self):
        self.__target_ui.label_target.debug_mode = not self.__target_ui.label_target.debug_mode
        self.__target_ui.label_target.update()

    def save(self):
        data = {
            'camera': {
                'width': self.__worker.available_width,
                'height': self.__worker.available_height
            },
            'shots': self.__target_ui.label_target.all_points
        }

        self.__filer.write_to_file(self.__target_ui.label_target.grab(), data)
        QMessageBox.about(self, "Saved", 'Data saved to the file')

    def load(self):
        file_path = QFileDialog.getOpenFileName(self, 'Open file', '{}'.format(self.__filer.data_path), '(*.json)')
        if len(file_path[0]) > 0:
            self.label_camera.all_points.clear()
            self.table_shots.clear()

            data = self.__filer.read_from_file(file_path[0])
            # self.init(data['camera'])
            for shot in data['shots']:
                self.bundler(shot)

    def change_background(self):
        file_name, _ = QFileDialog.getOpenFileName(parent=self,
                                                   caption='Select Backround Image',
                                                   directory='',
                                                   filter='Image Files (*.png *.jpg *.jpeg *.gif)')
        if file_name:
            self.__target_ui.label_target.set_background(QPixmap(file_name))
            self.__target_ui.label_target.update()
