from collections import OrderedDict
from functools import partial

from PyQt5.QtWidgets import QWidget,   \
                            QCheckBox, \
                            QVBoxLayout
from PyQt5.QtCore import Qt

from .. import image_tools
from . import stylesheets

class Filters(QWidget):
    """
    Subclass of QWidget. Contains pre-defined filters available im pillow.
    Only one filter at a time can be applied, except for the transparency
    filter which can be always applied.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.pic = parent.pic

        self.filters = OrderedDict()
        self.filters['BLUR'] = QCheckBox('Blur', self)
        self.filters['CONTOUR'] = QCheckBox('Contour', self)
        self.filters['DETAIL'] = QCheckBox('Detail', self)
        self.filters['EDGE_ENHANCE'] = QCheckBox('Edge enhance', self)
        self.filters['EDGE_ENHANCE_MORE'] = QCheckBox('More edge enhance', self)
        self.filters['EMBOSS'] = QCheckBox('Emboss', self)
        # This filter does not work properly with RGBA formats.
        # A workaround is used in self.apply.
        self.filters['FIND_EDGES'] = QCheckBox('Find edges', self)
        self.filters['SHARPEN'] = QCheckBox('Sharpen', self)
        self.filters['SMOOTH'] = QCheckBox('Smooth', self)
        self.filters['SMOOTH_MORE'] = QCheckBox('More smooth', self)

        self.transparency = QCheckBox('Transparency', self)

        vbox = QVBoxLayout()
        for filter_name, check_filter in self.filters.items():
            check_filter.setStyleSheet(stylesheets.check_box())
            check_filter.stateChanged.connect(partial(self.apply, filter_name))
            vbox.addWidget(check_filter)

        self.transparency.setStyleSheet(stylesheets.check_box())
        self.transparency.stateChanged.connect(self.make_pic_transparent)
        vbox.addWidget(self.transparency)
        vbox.setAlignment(Qt.AlignHCenter)
        self.setLayout(vbox)

    def apply(self, name, state):
        """
        Apply the chosen filter. Set all other filters (except for the transparency)
        to unchecked state (False).
        If the filter is uncheck, restore the image before the filter application.
        """
        if self.pic.image:
            if state == Qt.Checked:
                [f.setChecked(False) for n, f in self.filters.items() if n != name]
                self.pic.before_filter = self.pic.to_display
                alpha = self.pic.to_display.getchannel("A")
                self.pic.to_display = image_tools.apply_filter(self.pic, name)
                self.pic.to_display.putalpha(alpha)
            else:
                self.pic.to_display = self.pic.before_filter
            self.pic.update()

    def make_pic_transparent(self, state):
        """
        Make all white pixels transparent.
        If unchecked, restore white pixels.
        """
        if self.pic.image:
            if state == Qt.Checked:
                image_tools.make_transparent(self.pic)
            else:
                image_tools.reset_alpha(self.pic)
            self.pic.cache_colors = image_tools.get_modes(self.pic.to_display)
            self.pic.update()

    def reset(self, reset_tranparency = False):
        """
        Uncheck all filters (optionally reset also transparency).
        """
        for f in self.filters.values():
            f.setChecked(False)
        if reset_tranparency:
            self.transparency.setChecked(False)
