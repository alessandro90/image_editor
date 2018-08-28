from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QImage,       \
                        QImageReader, \
                        QPixmap
from PyQt5.QtCore import Qt

from .. import image_tools
from . import stylesheets

class Picture(QLabel):
    """
    Subclass of QLabel. It contains the image displayed on screen.
    """
    def __init__(self, parent):
        super().__init__('', parent)
        self.image = None
        self.name = None
        self.path = None
        self.extension = None
        self.to_display = None
        self.original = None
        self.original_alpha = None
        self.cache_colors = None
        self.white_pixels = None
        self.qim = None

        self.setMinimumSize(150, 150) # Minimum size of the displayed picture.
        self.setStyleSheet(stylesheets.label())

    def display_properties(self):
        """
        Display the image properties on the status tip when the mouse
        is over the image.
        """
        w, h = self.original.size
        self.setStatusTip(f'{w}x{h} pixels image ({self.extension})')

    def prep_image(self):
        """
        Prepare the image to be displayed on screen.
        """
        QImageReader.supportedImageFormats()
        self.original = image_tools.prepare_image(self.path, self)
        self.display_properties()
        self.to_display = self.original.copy()
        self.before_filter = self.original.copy()
        self.cache_colors = image_tools.get_modes(self.original)
        self.original_alpha = self.original.getchannel("A").copy()
        self.qt_tweaks()
        self.adjust_size()
        self.set_pixmap()          

    def adjust_size(self):
        """
        Rescale the displayed image every time it is necessary.
        """
        w = self.width()
        h = self.height()
        image = QPixmap.fromImage(self.qim)
        self.image = image.scaled(w, h, Qt.KeepAspectRatio)

    def qt_tweaks(self):
        """
        Workaround to display the image in linux as well as in
        windows.
        """
        # This is the only way to avoid a Windows crash.
        r, g, b, alpha =  image_tools.get_modes(self.to_display)
        image = image_tools.merge((b, g, r, alpha))
        data = image_tools.get_data(image)
        self.qim = QImage(data, image.size[0], image.size[1],
            QImage.Format_ARGB32)

    def set_pixmap(self):
        super().setPixmap(self.image)

    def update(self):
        """
        Update displayed image.
        """
        self.qt_tweaks()
        self.adjust_size()
        self.set_pixmap()

    def reset(self):
        """
        Remove the displayed image.
        """
        if self.image:
            self.qim = QImage()
            self.adjust_size()
            self.set_pixmap()
            self.to_display = None
            self.original = None
            self.image = None
            self.name = None
            self.path = None
            self.extension = None
            self.cache_colors = None

    def restore(self):
        """
        Display the original image.
        """
        if self.image:
            self.to_display = self.original.copy()
            self.cache_colors = image_tools.get_modes(self.original)
            self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image:
            self.adjust_size()
            self.set_pixmap()
