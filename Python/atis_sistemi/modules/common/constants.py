from PyQt5.QtCore import QSize, QPoint


class MainUIConstants:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 576
    SCREEN_MIN_WIDTH = 960

    INIT_POINT_GRID_BUTTONS = QPoint(970, 460)
    INIT_POINT_MENU_BAR = QPoint(0, 0)

    SIZE_GRID_BUTTONS = QSize(300, 80)
    SIZE_MENU_BAR = QSize(960, 20)

    FONT_SIZE_DEFAULT = 10

    SPACING_GRID_LAYOUT = 6


class LabelCameraConstants:
    INIT_POINT_LABEL_CAMERA = QPoint(0, 0)

    SIZE_LABEL_CAMERA = QSize(960, 540)
    SIZE_TARGET_MIN = QSize(480, 270)
    SIZE_TARGET_MAX = QSize(960, 540)
    SIZE_BULLET_HOLE = QSize(18, 18)


class TableShotsConstants:
    INIT_POINT_TABLE_SHOTS = QPoint(970, 10)

    SIZE_TABLE_SHOTS = QSize(300, 440)


class CameraConstants:
    CAMERA_ID = 0
    CAMERA_FPS = 60
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480

    DETECTION_DELAY_MS = 0.25


class DetectionConstants:
    LOWER_LEFT_RED = (0, 20, 20)
    UPPER_LEFT_RED = (10, 255, 255)

    LOWER_RIGHT_RED = (160, 20, 20)
    UPPER_RIGHT_RED = (180, 255, 255)

    SIGMA_X = 0
    KERNEL_SIZE = (5, 5)

    MIN_VALUE = 0
    MAX_VALUE = 255

    MIN_ADAPTIVE = 20
    MIN_CONTOUR_AREA = 10

    CANNY_THRESHOLD1 = 30
    CANNY_THRESHOLD2 = 200


class NetworkConstants:
    """Network configuration for Unreal Engine communication"""
    # Unreal Engine listening address
    HOST = "127.0.0.1"
    PORT = 7777
    
    # Protocol: "UDP" (low latency) or "TCP" (reliable)
    PROTOCOL = "UDP"
    
    # Enable/disable network transmission
    ENABLED = True
    
    # Heartbeat interval in seconds
    HEARTBEAT_INTERVAL = 5.0
