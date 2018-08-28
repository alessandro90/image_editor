from functools import partial

from PyQt5.QtWidgets import QWidget,     \
                            QPushButton, \
                            QGridLayout
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt

from .. import image_tools
from Modules.Gui.reset_slider import ResetSlider
from . import stylesheets

class Commands(QWidget):
    """
    Subclass of QWidget. It contains and displays all the sliders
    in the tab 'Sliders' along with the corresponding 'reset-buttons'.
    """
    def __init__(self, parent, pic, filters):
        super().__init__(parent)
        self.parent = parent
        self.pic = pic
        self.filters = filters
        self.sliders = []
        
        self.effects = {'Color'      : False,
                        'Brightness' : False,
                        'Contrast'   : False,
                        'Sharpness'  : False}
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
        contrast.setStatusTip('Reset contrast slider')
        contrast.setStyleSheet(stylesheets.button(bg = '#7d2fe1'))
        contrast.clicked.connect(self.effect_sliders['Contrast'].reset)

        color_balance = QPushButton('Color balance', self)
        color_balance.setStatusTip('Reset color-balance slider')
        color_balance.setStyleSheet(stylesheets.button(bg = '#2f95e1'))
        color_balance.clicked.connect(self.effect_sliders['Color'].reset)

        brightness = QPushButton('Brightness', self)
        brightness.setStatusTip('Reset brightness slider')
        brightness.setStyleSheet(stylesheets.button(bg = '#2fe180'))
        brightness.clicked.connect(self.effect_sliders['Brightness'].reset)

        sharpness = QPushButton('Sharpness', self)
        sharpness.setStatusTip('Reset sharpness slider')
        sharpness.setStyleSheet(stylesheets.button(bg = '#e1832f'))
        sharpness.clicked.connect(self.effect_sliders['Sharpness'].reset)

        reset_colors = QPushButton('Reset colors', self)
        reset_colors.setStatusTip('Reset rgb sliders')
        reset_colors.setStyleSheet(stylesheets.button())
        reset_colors.clicked.connect(self.reset_RGB_sliders)

        reset_all = QPushButton('Reset image', self)
        reset_all.setStatusTip('Back to original image')
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

    def set_effects(self):
        """
        Reset all effects (e.g., color-balance, contrast)
        """
        for k in self.effects.keys():
            self.effects[k] = False

    def adjust_size(self):
        """
        Resize the widget whether is needed.
        """
        for slider in self.sliders:
            slider.resize(10, self.parent.height() // 3)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_size()

    def reset_sliders(self):
        """
        Set all sliders to their default value.
        """
        for slider in self.sliders:
            slider.reset()

    def reset_RGB_sliders(self):
        """
        Reset only the red, green and blue sliders to
        their default value.
        """
        self.filters.reset()
        for slider in self.rgb_sliders.values():
            slider.reset()

    def make_RGB_sliders(self):
        """
        Initialize the red, green and blue sliders.
        """
        self.rgb_sliders = {}
        for color, html_color in zip(('red', 'green', 'blue'), 
                                     ('#ff0000', '#5dff00', '#0008ff')):
            self.rgb_sliders[color] = ResetSlider(0, -255, 255, Qt.Vertical)
            self.rgb_sliders[color].valueChanged.connect(
                partial(self.change_RGB, color, self.rgb_sliders[color])
            )
            self.rgb_sliders[color].setStyleSheet(
                stylesheets.slider_stylesheet(handle_color = '#FFFFFF', 
                                              groove_color_start = '#000000', 
                                              groove_color_stop = html_color)
            )
            self.rgb_sliders[color].setStatusTip(f'{color.capitalize()} slider')
            self.sliders.append(self.rgb_sliders[color])

    def make_effect_slider(self, *, effect, 
                           groove_color_stop,
                           handle_color = '#FFFFFF',
                           default = 1000, 
                           minv = 0, 
                           maxv = 3000, 
                           scale_factor = 1000):
        """
        Initialize the effects sliders (e.g., color-balance, contrast).
        """
        slider = ResetSlider(default, minv, maxv, scale_factor, Qt.Vertical)
        slider.valueChanged.connect(
            partial(self.change_effect, slider, effect)
        )
        slider.setStyleSheet(
            stylesheets.slider_stylesheet(handle_color = handle_color, 
                                          groove_color_stop = groove_color_stop)
        )
        if effect == 'Color':
            effect_name = effect + '-balance'
        else:
            effect_name = effect

        slider.setStatusTip(f"{effect_name} slider")
        self.sliders.append(slider)
        self.effect_sliders[effect] = slider

    def change_RGB(self, color, rgb_slider):
        """
        Change a color band by an amount equal to the value
        of the corresponding slider.
        """
        if self.pic.image:
            self.filters.reset()
            for slider in self.effect_sliders.values():
                slider.reset()
            self.set_effects()
            self.pic.to_display = image_tools.change_RGB_color(
                                    self.pic,
                                    color, 
                                    rgb_slider)
            self.pic.cache_colors = image_tools.get_modes(self.pic.to_display)
            self.pic.update()

    def change_effect(self, slider, effect):
        """
        Change an effect, by an amount equal to the
        corresponding slider value.
        """
        if self.pic.image:
            self.filters.reset()
            self.pic.to_display = image_tools.change_effect(
                                      self.pic, 
                                      slider, 
                                      effect, 
                                      self.effects)
            self.pic.update()

    def delete(self):
        """
        Remove the displayed image.
        """
        # Raises a warning but it doesn't seem harmful.
        self.reset_sliders()
        self.filters.reset(reset_tranparency = True)
        self.pic.reset()

    def total_reset(self):
        """
        Restore the originally loaded image.
        """
        self.reset_sliders()
        self.filters.reset(reset_tranparency = True)
        self.pic.restore()
