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
        
        self.setMinimumSize(150, 150) # Minimum size of the displayed picture.
        self.setStyleSheet(stylesheets.label())

    def get_image(self):
        self.prep_image()

    def display_properties(self):
        w, h = self.original.size
        self.setStatusTip(f'{w}x{h} pixels image ({self.path[-3:]})')

    def prep_image(self):
        QImageReader.supportedImageFormats()
        self.original = image_tools.prepare_image(self.path, self)
        self.display_properties()
        self.to_display = self.original.copy()
        self.before_filter = self.original.copy()
        self.cache_colors = image_tools.get_cache_colors(self)
        self.original_alpha = self.original.getchannel("A").copy()
        self.qt_tweaks()
        self.adjust_size()
        self.set_pixmap()          

    def adjust_size(self):
        w = self.width()
        h = self.height()
        image = QPixmap.fromImage(self.qim)
        self.image = image.scaled(w, h, Qt.KeepAspectRatio)

    def qt_tweaks(self):
        # This is the only way to avoid a Windows crash.
        r, g, b, alpha = self.to_display.split()
        image = image_tools.merge((b, g, r, alpha))
        data = image_tools.get_data(image)
        self.qim = QImage(data, image.size[0], image.size[1],
            QImage.Format_ARGB32)

    def set_pixmap(self):
        super().setPixmap(self.image)

    def update(self):
        self.qt_tweaks()
        self.adjust_size()
        self.set_pixmap()

    def reset(self):
        if self.image:
            self.qim = QImage()
            self.adjust_size()
            self.set_pixmap()
            self.to_display = None
            self.original = None
            self.image = None
            self.name = None
            self.path = None
            self.cache_colors = None

    def restore(self):
        if self.image:
            self.to_display = self.original.copy()
            self.cache_colors = image_tools.get_cache_colors(self)
            self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image:
            self.adjust_size()
            self.set_pixmap()
