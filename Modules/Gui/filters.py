from collections import OrderedDict
from functools import partial

from PyQt5.QtWidgets import QWidget,   \
                            QCheckBox, \
                            QVBoxLayout
from PyQt5.QtCore import Qt

from .. import image_tools
from . import stylesheets

class Filters(QWidget):
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
        if self.pic.image:
            if state == Qt.Checked:
                data = self.pic.to_display.getdata()
                trsp_image_data = []
                for pix in data:
                    if pix[:3] == (255, 255, 255):
                        trsp_image_data.append((255, 255, 255, 0))
                    else:
                        trsp_image_data.append(pix)
                # Because of this line, pic.original must always be
                # copied, otherwise putdata will modify also pic.original
                # since pic.to_display would point to pic.original.
                self.pic.to_display.putdata(trsp_image_data)
            else:
                self.pic.to_display.putalpha(self.pic.original_alpha)
            self.pic.cache_colors = self.pic.to_display.split()
            self.pic.update()

    def reset(self, reset_tranparency = False):
        for f in self.filters.values():
            f.setChecked(False)
        if reset_tranparency:
            self.transparency.setChecked(False)
