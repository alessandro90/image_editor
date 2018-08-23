from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt

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