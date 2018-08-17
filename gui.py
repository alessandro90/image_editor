import os
from functools import partial
from PyQt5.QtWidgets import QMainWindow, \
                            QWidget,     \
                            QLabel,      \
                            QGridLayout, \
                            QAction,     \
                            QFileDialog, \
                            QPushButton, \
                            QSizePolicy, \
                            QSlider
from PyQt5.QtGui import QImage,       \
                        QImageReader, \
                        QPixmap
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
        wid.setStyleSheet(stylesheets.main_window())

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

        self.newAction(fileMenu, 'Reset all', 'Ctrl+R', 'Reset picture', self.totalReset)

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
        if self.open_path and os.path.isdir(self.open_path):
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
        if self.save_path and os.path.isdir(self.save_path):
            save_folder = self.save_path
        else:
            save_folder = os.path.dirname(os.path.realpath(__file__))

        fname = QFileDialog.getSaveFileName(self, 'Save file as..', 
            save_folder, '*.png;; *jpg')
        if fname[0]:
            self.save_path, _ = os.path.split(fname[0])
            self.pic.name = fname[0]
            self.pic.to_display.save(self.pic.name)

    def totalReset(self):
        for slider in self.commands.sliders:
            slider.reset()
        self.pic.to_display = self.pic.original
        self.pic.update()


class Commands(QWidget):
    def __init__(self, parent, pic):
        super().__init__(parent)
        self.parent = parent
        self.pic = pic
        self.sliders = []


        self.makeContrastSlider()
        self.makeColorBalanceSlider()
        self.makeBrighnessSlider()
        self.makeSharpnessSlider()
        self.makeColorSliders()

        contrast = QPushButton('Contrast', self)
        contrast.setStyleSheet(stylesheets.button(bg = '#7d2fe1'))
        contrast.clicked.connect(lambda : self.contrast_slider.reset())

        color_balance = QPushButton('Color balance', self)
        color_balance.setStyleSheet(stylesheets.button(bg = '#2f95e1'))
        color_balance.clicked.connect(lambda : self.color_balance_slider.reset())

        brighness = QPushButton('Brighness', self)
        brighness.setStyleSheet(stylesheets.button(bg = '#2fe180'))
        brighness.clicked.connect(lambda : self.brighness_slider.reset())

        sharpness = QPushButton('Sharpness', self)
        sharpness.setStyleSheet(stylesheets.button(bg = '#e1832f'))
        sharpness.clicked.connect(lambda : self.sharpness_slider.reset())        

        reset_colors = QPushButton('Reset colors', self)
        reset_colors.setStyleSheet(stylesheets.button())
        reset_colors.clicked.connect(self.resetColorSliders)

        colors_grid = QGridLayout()
        colors_grid.addWidget(self.color_sliders['red'], 1, 0)
        colors_grid.addWidget(self.color_sliders['green'], 1, 1)
        colors_grid.addWidget(self.color_sliders['blue'], 1, 2)
        
        effects_grid = QGridLayout()
        effects_grid.addWidget(self.color_balance_slider, 0, 0)
        effects_grid.addWidget(self.contrast_slider, 0, 1)
        effects_grid.addWidget(self.brighness_slider, 0, 2)
        effects_grid.addWidget(self.sharpness_slider, 0, 3)

        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(0)
        buttons_grid.addWidget(reset_colors, 0, 0, 1, 2)
        buttons_grid.addWidget(color_balance, 1, 0)
        buttons_grid.addWidget(contrast, 1, 1)
        buttons_grid.addWidget(brighness, 2, 0)
        buttons_grid.addWidget(sharpness, 2, 1)

        meta_grid = QGridLayout()
        meta_grid.addLayout(colors_grid, 0, 0, Qt.AlignHCenter)
        meta_grid.addLayout(effects_grid, 1, 0, Qt.AlignHCenter)
        meta_grid.addLayout(buttons_grid, 2, 0, Qt.AlignHCenter)

        self.setLayout(meta_grid)

    def adjustSize(self):
        for slider in self.sliders:
            slider.resize(10, self.parent.height() // 3)

    def resizeEvent(self, event):
        self.adjustSize()

    def resetSliders(self):
        for slider in self.sliders:
            slider.reset()

    def resetColorSliders(self):
        for slider in self.color_sliders.values():
            slider.reset()

    def makeColorSliders(self):
        self.color_sliders = {}
        for color, html_color in zip(('red', 'green', 'blue'), 
            ('#ff0000', '#5dff00', '#0008ff')):
            self.color_sliders[color] = ResetSlider(0, -255, 255, Qt.Vertical)
            self.color_sliders[color].valueChanged.connect(
                partial(self.pic.changeColor, color, 
                    self.color_sliders[color], 
                    self.color_balance_slider, 
                    self.contrast_slider, 
                    self.brighness_slider, 
                    self.sharpness_slider)
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
            stylesheets.slider_stylesheet(handle_color = '#FFFFFF', groove_color_stop = '#2f95e1')
        )
        self.sliders.append(self.color_balance_slider)

    def makeContrastSlider(self):
        self.contrast_slider = ResetSlider(1000, 0, 2000, 
            1000, Qt.Vertical)
        self.contrast_slider.valueChanged.connect(
            partial(self.pic.changeContrast, self.contrast_slider)
        )
        self.contrast_slider.setStyleSheet(
            stylesheets.slider_stylesheet(handle_color = '#FFFFFF', groove_color_stop = '#7d2fe1')
        )
        self.sliders.append(self.contrast_slider)

    def makeBrighnessSlider(self):
        self.brighness_slider = ResetSlider(1000, 0, 2000, 
            1000, Qt.Vertical)
        self.brighness_slider.valueChanged.connect(
            partial(self.pic.changeBrighness, self.brighness_slider)
        )
        self.brighness_slider.setStyleSheet(
            stylesheets.slider_stylesheet(handle_color = '#FFFFFF', groove_color_stop = '#2fe180')
        )
        self.sliders.append(self.brighness_slider)

    def makeSharpnessSlider(self):
        self.sharpness_slider = ResetSlider(1000, 0, 2000, 
            1000, Qt.Vertical)
        self.sharpness_slider.valueChanged.connect(
            partial(self.pic.changeSharpness, self.sharpness_slider)
        )
        self.sharpness_slider.setStyleSheet(
            stylesheets.slider_stylesheet(handle_color = '#FFFFFF', groove_color_stop = '#e1832f')
        )
        self.sliders.append(self.sharpness_slider)


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
        self.changed_brighness = False
        self.changed_sharpness = False
        self.qtTweaks()
        self.adjustSize()
        self.setPixmap()

    def changeColor(self, color, color_slider, color_balance_slider, 
        contrast_slider, brighness_slider, sharpness_slider):
        if self.image:
            color_balance_slider.reset()
            contrast_slider.reset()
            brighness_slider.reset()
            sharpness_slider.reset()
            self.to_display, self.cache_colors = image_tools.change_color(self, 
                color, 
                color_slider)
            self.update()

    def changeColorBalance(self, slider):
        if self.image:
            self.to_display = image_tools.change_color_balance(self, slider)
            self.update()

    def changeContrast(self, slider):
        if self.image:
            self.to_display = image_tools.change_contrast(self, slider)
            self.update()

    def changeBrighness(self, slider):
        if self.image:
            self.to_display = image_tools.change_brightness(self, slider)
            self.update()

    def changeSharpness(self, slider):
        if self.image:
            self.to_display = image_tools.change_sharpness(self, slider)
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
