import os
from functools import partial
from PyQt5.QtWidgets import QMainWindow, \
                            QWidget,     \
                            QLabel,      \
                            QGridLayout, \
                            QAction,     \
                            QFileDialog, \
                            QSizePolicy, \
                            QSlider
from PyQt5.QtGui import QImage,       \
                        QImageReader, \
                        QPixmap,      \
                        QIcon
from PyQt5.QtCore import Qt

import ImageTools
import stylesheets

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        wid = QWidget()
        self.setCentralWidget(wid)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.gray)
        self.setPalette(palette)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        self.add_action(fileMenu, 'Open', 'Ctrl+O', 'Open new file', 
            self.showOpenDialog)
        self.add_action(fileMenu, 'Save as..', 'Ctrl+Shift+S', 'Save file as..', 
            self.showSaveDialog)
        self.add_action(fileMenu, 'Save', 'Ctrl+S', 'Save file', self.saveCurrent)

        self.pic = Picture(self)
        self.commands = Commands(self, self.pic)
  
        grid = QGridLayout()
        grid.addWidget(self.commands, 0, 0)
        grid.setSpacing(10)
        grid.addWidget(self.pic, 0, 1)

        wid.setLayout(grid)
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Insert Image Test')
        self.show()

    def add_action(self, fileMenu, name, shortcut, statustip, connection):
        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.setStatusTip(statustip)
        action.triggered.connect(connection)
        fileMenu.addAction(action)

    def showOpenDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 
        os.path.dirname(os.path.realpath(__file__)), '*png *jpg;; *.png;; *jpg')
        if fname[0]:
            self.pic.get_image(fname[0])
            self.pic.name = None
            self.commands.reset_sliders()

    def saveCurrent(self):
        if self.pic.name:
            self.pic.to_display.save(self.pic.name)
        else:
            self.showSaveDialog()

    def showSaveDialog(self):
        save_folder = self.pic.name or os.path.dirname(os.path.realpath(__file__))
        fname = QFileDialog.getSaveFileName(self, 'Save file as..', 
            save_folder, '*.png;; *jpg')
        if fname[0]:
            self.pic.name = fname[0]
            self.pic.to_display.save(self.pic.name)


class Commands(QWidget):
    def __init__(self, parent, pic):
        super().__init__(parent)
        self.parent = parent
        self.pic = pic
        self.sliders = {}

        self.make_contrast_slider()
        self.make_color_balance_slider()
        self.make_color_sliders()

        grid = QGridLayout()
        for i, slider in enumerate(self.color_sliders.values()):
            grid.addWidget(slider, 0, i)
        grid.addWidget(self.color_balance_slider, 1, 0)
        grid.addWidget(self.contrast_slider, 1, 1)

        self.setLayout(grid)

    def adjust_size(self):
        for slider in self.color_sliders.values():
            slider.resize(10, self.parent.height() // 3)

    def resizeEvent(self, event):
        self.adjust_size()

    def reset_sliders(self):
        for slider in self.sliders["RGB"]:
            slider.setValue((abs(slider.maximum()) - abs(slider.minimum())) // 2)
        self.sliders["CB"].setValue(1000)
        self.sliders["C"].setValue(1000)


    def make_color_sliders(self):
        self.color_sliders = {}
        for color, html_color in zip(('red', 'green', 'blue'), ('#ff0000', '#5dff00', '#0008ff')):
            self.color_sliders[color] = QSlider(Qt.Vertical)
            self.color_sliders[color].setFocusPolicy(Qt.NoFocus)
            self.color_sliders[color].setRange(-255, 255)
            self.color_sliders[color].setValue(0)
            self.color_sliders[color].valueChanged.connect(
                partial(self.pic.changeColor, color, self.color_sliders[color], 
                    self.color_balance_slider, self.contrast_slider)
            )
            
            self.color_sliders[color].setStyleSheet(
                stylesheets.slider_stylesheet(handle_color = '#FFFFFF', 
                                              groove_color_start = '#000000', 
                                              groove_color_stop = html_color)
            )
            try:
                self.sliders["RGB"].append(self.color_sliders[color])
            except KeyError:
                self.sliders["RGB"] = [self.color_sliders[color]]

    def make_color_balance_slider(self):
        self.color_balance_slider = QSlider(Qt.Vertical)
        self.color_balance_slider.setFocusPolicy(Qt.NoFocus)
        self.color_balance_slider.setRange(0, 2000)
        self.color_balance_slider.setValue(1000)
        self.color_balance_slider.valueChanged.connect(
            partial(self.pic.changeColorBalance, self.color_balance_slider)
        )
        self.color_balance_slider.setStyleSheet(
            stylesheets.slider_stylesheet()
        )
        self.sliders["CB"] = self.color_balance_slider

    def make_contrast_slider(self):
        self.contrast_slider = QSlider(Qt.Vertical)
        self.contrast_slider.setFocusPolicy(Qt.NoFocus)
        self.contrast_slider.setRange(0, 2000)
        self.contrast_slider.setValue(1000)
        self.contrast_slider.valueChanged.connect(
            partial(self.pic.changeContrast, self.contrast_slider)
        )
        self.contrast_slider.setStyleSheet(
            stylesheets.slider_stylesheet()
        )
        self.sliders["C"] = self.contrast_slider


class Picture(QLabel):
    def __init__(self, parent):
        super().__init__('', parent)
        self.image = None
        self.name = None
        self.path = None
        self.parent = parent
        self.setMinimumSize(150, 150) # Minimum size of the displayed picture.

    def get_image(self, fname):
        self.prep_image(fname)

    def prep_image(self, fname):
        QImageReader.supportedImageFormats()
        self.original = ImageTools.prepare_image(fname, self)
        self.to_display = ImageTools.copy(self.original)
        self.cache_colors = ImageTools.get_cache_colors(self)
        self.copy_color_balance = False
        self.copy_contrast = False
        self.qt_tweaks()
        self.adjust_size()
        self.setPixmap()

    def changeColor(self, color, directional_slider, color_balance_slider, 
        contrast_slider):
        if self.image:
            color_balance_slider.setValue(1000)
            contrast_slider.setValue(1000)
            self.to_display, self.cache_colors = ImageTools.change_color(self, 
                color, 
                directional_slider)
            self.update()

    def changeColorBalance(self, slider):
        if self.image:
            self.to_display, self.copy_color_balance = ImageTools.change_color_balance(self, slider)
            self.copy_color_balance = ImageTools.copy(self.to_display)
            self.update()

    def changeContrast(self, slider):
        if self.image:
            self.to_display, self.copy_contrast = ImageTools.change_contrast(self, slider)
            self.copy_contrast = ImageTools.copy(self.to_display)
            self.update()

    def adjust_size(self):
        w = self.parent.width()
        h = self.parent.height()
        image = QPixmap.fromImage(self.qim)
        self.image = image.scaled(3 * w // 4, h, Qt.KeepAspectRatio)

    def qt_tweaks(self):
        # This is the only way to avoid a Windows crash.
        r, g, b = self.to_display.split()
        image = ImageTools.merge((b, g, r))
        data = ImageTools.get_data(image)
        self.qim = QImage(data, image.size[0], image.size[1],
            QImage.Format_ARGB32)

    def setPixmap(self):
        super().setPixmap(self.image)

    def update(self):
        self.qt_tweaks()
        self.adjust_size()
        self.setPixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image:
            self.adjust_size()
            self.setPixmap()
