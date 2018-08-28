"""
Run this script to start the application.
"""

import sys
from PyQt5.QtWidgets import QApplication
from Modules.Gui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())
