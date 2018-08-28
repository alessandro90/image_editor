from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt

class ResetSlider(QSlider):
    """
    Subclass of QSlider. It can be reset to a default value.
    If a scale-factor is given, values from value() functions
    are scaled accordingly.
    """
    def __init__(self, default_value, minv, maxv, scale_factor = None, *args):
        super().__init__(*args)
        self.default_value = default_value
        self.scale_factor = scale_factor
        self.setFocusPolicy(Qt.NoFocus)
        self.setRange(minv, maxv)
        self.setValue(self.default_value)

    def reset(self):
        """
        Reset to default value.
        """
        self.setValue(self.default_value)

    def value(self):
        """
        Returns the current slider value.
        """
        if self.scale_factor:
            return super().value() / self.scale_factor
        else:
            return super().value()