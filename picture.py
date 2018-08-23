from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QImage,       \
                        QImageReader, \
                        QPixmap
from PyQt5.QtCore import Qt

import image_tools
import stylesheets

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
        self.before_filter = self.original
        self.cache_colors = image_tools.get_cache_colors(self)
        self.qt_tweaks()
        self.adjust_size()
        self.set_pixmap()

    def change_RGB(self, color, rgb_slider, color_slider, 
        contrast_slider, brightness_slider, sharpness_slider):
        if self.image:
            self.parent.filters.reset()
            color_slider.reset()
            contrast_slider.reset()
            brightness_slider.reset()
            sharpness_slider.reset()
            self.set_effects()
            self.to_display, self.cache_colors = image_tools.change_RGB_color(
                self,
                color, 
                rgb_slider)
            self.update()

    def change_effect(self, slider, effect):
        if self.image:
            self.parent.filters.reset()
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
