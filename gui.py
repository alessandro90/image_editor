from collections import OrderedDict
import os
from functools import partial
from PyQt5.QtWidgets import QMainWindow, \
                            QWidget,     \
                            QLabel,      \
                            QGridLayout, \
                            QVBoxLayout, \
                            QAction,     \
                            QFileDialog, \
                            QPushButton, \
                            QSizePolicy, \
                            QSlider,     \
                            QTabWidget,  \
                            QCheckBox
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
        self.new_action(fileMenu, 'Open', 'Ctrl+O', 'Open new file', 
            self.show_open_dialog)
        self.new_action(fileMenu, 'Save as..', 'Ctrl+Shift+S', 'Save file as..', 
            self.show_save_dialog)
        self.new_action(fileMenu, 'Save', 'Ctrl+S', 'Save file', self.save_current)

        self.pic = Picture(self)
        policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.pic.setSizePolicy(policy)

        self.commands = Commands(self, self.pic)

        self.filters = Filters(self)

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
        open_path, '*png *jpg;; *.png;; *jpg')
        if fname[0]:
            self.open_path, _ = os.path.split(fname[0])
            self.pic.get_image(fname[0])
            self.pic.name = None
            self.commands.reset_sliders()

    def save_current(self):
        if self.pic.name:
            self.pic.to_display.save(self.pic.name)
        else:
            self.show_save_dialog()

    def show_save_dialog(self):
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


class Filters(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pic = self.parent.pic

        self.filters = OrderedDict()
        self.filters['BLUR'] = QCheckBox('Blur', self)
        self.filters['CONTOUR'] = QCheckBox('Contour', self)
        self.filters['DETAIL'] = QCheckBox('Detail', self)
        self.filters['EDGE_ENHANCE'] = QCheckBox('Edge enhance', self)
        self.filters['EDGE_ENHANCE_MORE'] = QCheckBox('More edge enhance', self)
        self.filters['EMBOSS'] = QCheckBox('Emboss', self)
        self.filters['FIND_EDGES'] = QCheckBox('Find edges', self)
        self.filters['SHARPEN'] = QCheckBox('Sharpen', self)
        self.filters['SMOOTH'] = QCheckBox('Smooth', self)
        self.filters['SMOOTH_MORE'] = QCheckBox('More smooth', self)

        vbox = QVBoxLayout()
        for filter_name, check_filter in self.filters.items():
            check_filter.setStyleSheet(stylesheets.check_box())
            # check_filter.stateChanged.connect(partial(self.applyFilter, name))
            vbox.addWidget(check_filter)
        vbox.setAlignment(Qt.AlignHCenter)
        self.setLayout(vbox)

    # def applyFilter(self, name):



class Commands(QWidget):
    def __init__(self, parent, pic):
        super().__init__(parent)
        self.parent = parent
        self.pic = pic
        self.sliders = []
        self.effect_sliders = {}

        self.make_effect_slider(effect = 'Contrast',
                              groove_color_stop = '#7d2fe1')
        self.make_effect_slider(effect = 'Color',
                              groove_color_stop = '#2f95e1')
        self.make_effect_slider(effect = 'Brightness',
                              groove_color_stop = '#2fe180')
        self.make_effect_slider(effect = 'Sharpness',
                              groove_color_stop = '#e1832f')
        # Call _after_ all make_effect_slider calls.
        self.make_RGB_sliders()

        contrast = QPushButton('Contrast', self)
        contrast.setStyleSheet(stylesheets.button(bg = '#7d2fe1'))
        contrast.clicked.connect(self.effect_sliders['Contrast'].reset)

        color_balance = QPushButton('Color balance', self)
        color_balance.setStyleSheet(stylesheets.button(bg = '#2f95e1'))
        color_balance.clicked.connect(self.effect_sliders['Color'].reset)

        brightness = QPushButton('Brightness', self)
        brightness.setStyleSheet(stylesheets.button(bg = '#2fe180'))
        brightness.clicked.connect(self.effect_sliders['Brightness'].reset)

        sharpness = QPushButton('Sharpness', self)
        sharpness.setStyleSheet(stylesheets.button(bg = '#e1832f'))
        sharpness.clicked.connect(self.effect_sliders['Sharpness'].reset)

        reset_colors = QPushButton('Reset colors', self)
        reset_colors.setStyleSheet(stylesheets.button())
        reset_colors.clicked.connect(self.reset_RGB_sliders)

        reset_all = QPushButton('Reset image', self)
        reset_all.setStyleSheet(stylesheets.button())
        reset_all.clicked.connect(self.total_reset)

        colors_grid = QGridLayout()
        colors_grid.addWidget(self.rgb_sliders['red'], 1, 0)
        colors_grid.addWidget(self.rgb_sliders['green'], 1, 1)
        colors_grid.addWidget(self.rgb_sliders['blue'], 1, 2)
        
        effects_grid = QGridLayout()
        effects_grid.addWidget(self.effect_sliders['Color'], 0, 0)
        effects_grid.addWidget(self.effect_sliders['Contrast'], 0, 1)
        effects_grid.addWidget(self.effect_sliders['Brightness'], 0, 2)
        effects_grid.addWidget(self.effect_sliders['Sharpness'], 0, 3)

        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(0)
        buttons_grid.addWidget(reset_all, 0, 0, 1, 2)
        buttons_grid.addWidget(reset_colors, 1, 0, 1, 2)
        buttons_grid.addWidget(color_balance, 2, 0)
        buttons_grid.addWidget(contrast, 2, 1)
        buttons_grid.addWidget(brightness, 3, 0)
        buttons_grid.addWidget(sharpness, 3, 1)

        meta_grid = QGridLayout()
        meta_grid.addLayout(colors_grid, 0, 0, Qt.AlignHCenter)
        meta_grid.addLayout(effects_grid, 1, 0, Qt.AlignHCenter)
        meta_grid.addLayout(buttons_grid, 2, 0, Qt.AlignHCenter)

        self.setLayout(meta_grid)

    def adjust_size(self):
        for slider in self.sliders:
            slider.resize(10, self.parent.height() // 3)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_size()

    def reset_sliders(self):
        for slider in self.sliders:
            slider.reset()

    def reset_RGB_sliders(self):
        for slider in self.rgb_sliders.values():
            slider.reset()

    def make_RGB_sliders(self):
        self.rgb_sliders = {}
        for color, html_color in zip(('red', 'green', 'blue'), 
                                     ('#ff0000', '#5dff00', '#0008ff')):
            self.rgb_sliders[color] = ResetSlider(0, -255, 255, Qt.Vertical)
            self.rgb_sliders[color].valueChanged.connect(
                partial(self.pic.change_RGB, color, 
                        self.rgb_sliders[color], 
                        self.effect_sliders['Color'], 
                        self.effect_sliders['Contrast'], 
                        self.effect_sliders['Brightness'], 
                        self.effect_sliders['Sharpness']
                )
            )
            self.rgb_sliders[color].setStyleSheet(
                stylesheets.slider_stylesheet(handle_color = '#FFFFFF', 
                                              groove_color_start = '#000000', 
                                              groove_color_stop = html_color)
            )
            self.sliders.append(self.rgb_sliders[color])

    def make_effect_slider(self, *, effect, 
                         groove_color_stop,
                         handle_color = '#FFFFFF',
                         default = 1000, 
                         minv = 0, 
                         maxv = 2000, 
                         scale_factor = 1000):
        slider = ResetSlider(default, 
                             minv, 
                             maxv, 
                             scale_factor, 
                             Qt.Vertical)
        slider.valueChanged.connect(
            partial(self.pic.change_effect, slider, effect)
        )
        slider.setStyleSheet(
            stylesheets.slider_stylesheet(handle_color = handle_color, 
                                          groove_color_stop = groove_color_stop)
        )
        self.sliders.append(slider)
        self.effect_sliders[effect] = slider

    def delete(self):
        # Raises a warning but it doesn't seem harmful.
        self.reset_sliders()
        if self.pic.image:
            self.pic.qim = QImage()
            self.pic.adjust_size()
            self.pic.set_pixmap()
            self.pic.to_display = None
            self.pic.original = None
            self.pic.image = None
            self.pic.name = None
            self.pic.path = None
            self.pic.cache_colors = None

    def total_reset(self):
        self.reset_sliders()
        if self.pic.image:
            self.pic.to_display = self.pic.original
            self.pic.cache_colors = image_tools.get_cache_colors(self.pic)
            self.pic.update()


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
        self.effects = {'Color' : 'changed_rgb',
                        'Brightness' : 'changed_brightness',
                        'Contrast' : 'changed_contrast',
                        'Sharpness' : 'changed_sharpness'}
        self.set_effects()
        self.setMinimumSize(150, 150) # Minimum size of the displayed picture.
        self.setStyleSheet(stylesheets.label())

    def set_effects(self):
        for v in self.effects.values():
            setattr(self, v, False)

    def get_image(self, fname):
        self.prep_image(fname)

    def prep_image(self, fname):
        QImageReader.supportedImageFormats()
        self.original = image_tools.prepare_image(fname, self)
        self.to_display = self.original
        self.cache_colors = image_tools.get_cache_colors(self)
        self.qt_tweaks()
        self.adjust_size()
        self.set_pixmap()

    def change_RGB(self, color, rgb_slider, color_slider, 
        contrast_slider, brightness_slider, sharpness_slider):
        if self.image:
            color_slider.reset()
            contrast_slider.reset()
            brightness_slider.reset()
            sharpness_slider.reset()
            self.set_effects()
            self.to_display, self.cache_colors = image_tools.change_color(
                self,
                color, 
                rgb_slider)
            self.update()

    def change_effect(self, slider, effect):
        if self.image:
            self.to_display = image_tools.change_effect(self, slider, effect)
            self.update()           

    def adjust_size(self):
        w = self.parent.width()
        h = self.parent.height()
        image = QPixmap.fromImage(self.qim)
        self.image = image.scaled(3 * w // 4, h, Qt.KeepAspectRatio)

    def qt_tweaks(self):
        # This is the only way to avoid a Windows crash.
        r, g, b = self.to_display.split()
        image = image_tools.merge((b, g, r))
        data = image_tools.get_data(image)
        self.qim = QImage(data, image.size[0], image.size[1],
            QImage.Format_ARGB32)

    def set_pixmap(self):
        super().setPixmap(self.image)

    def update(self):
        self.qt_tweaks()
        self.adjust_size()
        self.set_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image:
            self.adjust_size()
            self.set_pixmap()
