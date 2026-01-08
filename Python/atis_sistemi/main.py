from PyQt5 import QtWidgets

from modules.main.main_ui import MainUI

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = MainUI()
    sys.exit(app.exec_())
