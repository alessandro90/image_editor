import os
from PyQt5.QtWidgets import qApp,        \
                            QMainWindow, \
                            QWidget,     \
                            QGridLayout, \
                            QAction,     \
                            QFileDialog, \
                            QSizePolicy, \
                            QTabWidget
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt

import stylesheets
from commands import Commands
from filters import Filters
from picture import Picture

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.save_path = None
        self.open_path = None
        wid = QWidget()
        self.setCentralWidget(wid)
        wid.setStyleSheet(stylesheets.main_window())

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        self.new_action(fileMenu, 'Open', 'Ctrl+O', 'Open new file', 
            self.show_open_dialog)
        self.new_action(fileMenu, 'Save as..', 'Ctrl+Shift+S', 'Save file as..', 
            self.show_save_dialog)
        self.new_action(fileMenu, 'Save', 'Ctrl+S', 'Save file', self.save_current)
        self.new_action(fileMenu, 'Exit', None, 'Exit application', qApp.quit)

        self.pic = Picture(self)
        policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.pic.setSizePolicy(policy)

        self.filters = Filters(self)

        self.commands = Commands(self, self.pic, self.filters)

        imageMenu = menubar.addMenu('&Image')
        self.new_action(imageMenu, 
                       'Reset image', 
                       'Ctrl+R', 
                       'Reset image', 
                       self.commands.total_reset)
        self.new_action(imageMenu, 
                       'Clear', 
                       'Ctrl+C', 
                       'Remove image', 
                       self.commands.delete)

        self.commands_panel = QTabWidget()
        policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.commands_panel.setSizePolicy(policy)

        self.commands_panel.addTab(self.commands, 'Sliders')
        self.commands_panel.addTab(self.filters, 'Filters')

        grid = QGridLayout()
        grid.addWidget(self.commands_panel, 0, 0)
        grid.setSpacing(10)
        grid.addWidget(self.pic, 0, 1)

        wid.setLayout(grid)
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Pycture')
        self.show()

    def new_action(self, menu, name, shortcut, statustip, connection):
        action = QAction(name, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.setStatusTip(statustip)
        action.triggered.connect(connection)
        menu.addAction(action)

    def show_open_dialog(self):
        if self.open_path and os.path.isdir(self.open_path):
            open_path = self.open_path
        else:
            open_path = os.path.dirname(os.path.realpath(__file__))
        fname = QFileDialog.getOpenFileName(self, 'Open file', 
        open_path, '*png *jpg *tif;; *.png;; *jpg;; *tif')
        if fname[0]:
            self.open_path, _ = os.path.split(fname[0])
            self.pic.path = fname[0]
            self.pic.get_image()
            self.pic.name = None
            self.commands.reset_sliders()
            self.filters.reset()
            self.filters.transparency.setChecked(False)

    def save_current(self):
        if self.pic.name:
            self.pic.to_display.save(self.pic.name)
        else:
            self.show_save_dialog()

    def show_save_dialog(self):
        if self.pic.image:
            if self.save_path and os.path.isdir(self.save_path):
                save_folder = self.save_path
            else:
                save_folder = os.path.dirname(os.path.realpath(__file__))
    
            fname = QFileDialog.getSaveFileName(self, 'Save file as..', 
                save_folder, '*.png;; *jpg;; *tif')
            if fname[0]:
                self.save_path, _ = os.path.split(fname[0])
                self.pic.name = fname[0]
                self.pic.to_display.save(self.pic.name)
