from collections import OrderedDict
from functools import partial

from PyQt5.QtWidgets import QWidget,   \
                            QCheckBox, \
                            QVBoxLayout
from PyQt5.QtCore import Qt

import image_tools
import stylesheets

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
        self.filters['FIND_EDGES'] = QCheckBox('Find edges', self)
        self.filters['SHARPEN'] = QCheckBox('Sharpen', self)
        self.filters['SMOOTH'] = QCheckBox('Smooth', self)
        self.filters['SMOOTH_MORE'] = QCheckBox('More smooth', self)

        vbox = QVBoxLayout()
        for filter_name, check_filter in self.filters.items():
            check_filter.setStyleSheet(stylesheets.check_box())
            check_filter.stateChanged.connect(partial(self.apply, filter_name))
            vbox.addWidget(check_filter)
        vbox.setAlignment(Qt.AlignHCenter)
        self.setLayout(vbox)

    def apply(self, name, state):
        if self.pic.image:
            if state == Qt.Checked:
                [f.setChecked(False) for n, f in self.filters.items() if n != name]
                self.pic.before_filter = self.pic.to_display
                self.pic.to_display = image_tools.apply_filter(self.pic, name)
                self.pic.update()
            else:
                self.pic.to_display = self.pic.before_filter
                self.pic.update()

    def reset(self):
        for f in self.filters.values():
            f.setChecked(False)
