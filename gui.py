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

import image_tools
import stylesheets

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.save_path = None
        self.open_path = None
        wid = QWidget()
        self.setCentralWidget(wid)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.gray)
        self.setPalette(palette)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        self.newAction(fileMenu, 'Open', 'Ctrl+O', 'Open new file', 
            self.showOpenDialog)
        self.newAction(fileMenu, 'Save as..', 'Ctrl+Shift+S', 'Save file as..', 
            self.showSaveDialog)
        self.newAction(fileMenu, 'Save', 'Ctrl+S', 'Save file', self.saveCurrent)

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

    def newAction(self, fileMenu, name, shortcut, statustip, connection):
        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.setStatusTip(statustip)
        action.triggered.connect(connection)
        fileMenu.addAction(action)

    def showOpenDialog(self):
        if self.open_path:
            open_path = self.open_path
        else:
            open_path = os.path.dirname(os.path.realpath(__file__))
        fname = QFileDialog.getOpenFileName(self, 'Open file', 
        open_path, '*png *jpg;; *.png;; *jpg')
        if fname[0]:
            self.open_path, _ = os.path.split(fname[0])
            self.pic.get_image(fname[0])
            self.pic.name = None
            self.commands.resetSliders()

    def saveCurrent(self):
        if self.pic.name:
            self.pic.to_display.save(self.pic.name)
        else:
            self.showSaveDialog()

    def showSaveDialog(self):
        if not self.save_path:
            save_folder = os.path.dirname(os.path.realpath(__file__))
        else:
            save_folder = self.save_path

        fname = QFileDialog.getSaveFileName(self, 'Save file as..', 
            save_folder, '*.png;; *jpg')
        if fname[0]:
            self.save_path, _ = os.path.split(fname[0])
            self.pic.name = fname[0]
            self.pic.to_display.save(self.pic.name)


class Commands(QWidget):
    def __init__(self, parent, pic):
        super().__init__(parent)
        self.parent = parent
        self.pic = pic
        self.sliders = []

        self.makeContrastSlider()
        self.makeColorBalanceSlider()
        self.makeColorSliders()

        grid = QGridLayout()
        for i, slider in enumerate(self.color_sliders.values()):
            grid.addWidget(slider, 0, i)
        grid.addWidget(self.color_balance_slider, 1, 0)
        grid.addWidget(self.contrast_slider, 1, 1)

        self.setLayout(grid)

    def adjustSize(self):
        for slider in self.sliders:
            slider.resize(10, self.parent.height() // 3)

    def resizeEvent(self, event):
        self.adjustSize()

    def resetSliders(self):
        for slider in self.sliders:
            slider.reset()


    def makeColorSliders(self):
        self.color_sliders = {}
        for color, html_color in zip(('red', 'green', 'blue'), 
            ('#ff0000', '#5dff00', '#0008ff')):
            self.color_sliders[color] = ResetSlider(0, -255, 255, Qt.Vertical)
            self.color_sliders[color].valueChanged.connect(
                partial(self.pic.changeColor, color, self.color_sliders[color], 
                    self.color_balance_slider, self.contrast_slider)
            )
            
            self.color_sliders[color].setStyleSheet(
                stylesheets.slider_stylesheet(handle_color = '#FFFFFF', 
                                              groove_color_start = '#000000', 
                                              groove_color_stop = html_color)
            )
            self.sliders.append(self.color_sliders[color])

    def makeColorBalanceSlider(self):
        self.color_balance_slider = ResetSlider(1000, 0, 2000, 
            1000, Qt.Vertical)
        self.color_balance_slider.valueChanged.connect(
            partial(self.pic.changeColorBalance, self.color_balance_slider)
        )
        self.color_balance_slider.setStyleSheet(
            stylesheets.slider_stylesheet()
        )
        self.sliders.append(self.color_balance_slider)

    def makeContrastSlider(self):
        self.contrast_slider = ResetSlider(1000, 0, 2000, 
            1000, Qt.Vertical)
        self.contrast_slider.valueChanged.connect(
            partial(self.pic.changeContrast, self.contrast_slider)
        )
        self.contrast_slider.setStyleSheet(
            stylesheets.slider_stylesheet()
        )
        self.sliders.append(self.contrast_slider)


class ResetSlider(QSlider):
    def __init__(self, default_value, minv, maxv, scale_factor = None, *args):
        super().__init__(*args)
        self.default_value = default_value
        self.scale_factor = scale_factor
        self.setFocusPolicy(Qt.NoFocus)
        self.setRange(minv, maxv)
        self.setValue(self.default_value)

    def reset(self):
        self.setValue(self.default_value)

    def value(self):
        if self.scale_factor:
            return super().value() / self.scale_factor
        else:
            return super().value()


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
        self.original = image_tools.prepare_image(fname, self)
        self.to_display = image_tools.copy(self.original)
        self.cache_colors = image_tools.get_cache_colors(self)
        self.changed_color_balance = False
        self.changed_contrast = False
        self.qtTweaks()
        self.adjustSize()
        self.setPixmap()

    def changeColor(self, color, directional_slider, color_balance_slider, 
        contrast_slider):
        if self.image:
            color_balance_slider.reset()
            contrast_slider.reset()
            self.to_display, self.cache_colors = image_tools.change_color(self, 
                color, 
                directional_slider)
            self.update()

    def changeColorBalance(self, slider):
        if self.image:
            self.to_display = image_tools.change_color_balance(self, slider)
            self.update()

    def changeContrast(self, slider):
        if self.image:
            self.to_display = image_tools.change_contrast(self, slider)
            self.update()

    def adjustSize(self):
        w = self.parent.width()
        h = self.parent.height()
        image = QPixmap.fromImage(self.qim)
        self.image = image.scaled(3 * w // 4, h, Qt.KeepAspectRatio)

    def qtTweaks(self):
        # This is the only way to avoid a Windows crash.
        r, g, b = self.to_display.split()
        image = image_tools.merge((b, g, r))
        data = image_tools.get_data(image)
        self.qim = QImage(data, image.size[0], image.size[1],
            QImage.Format_ARGB32)

    def setPixmap(self):
        super().setPixmap(self.image)

    def update(self):
        self.qtTweaks()
        self.adjustSize()
        self.setPixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image:
            self.adjustSize()
            self.setPixmap()
