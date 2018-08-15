import os
from functools import partial
from PyQt5.QtWidgets import QMainWindow, \
                            QWidget,     \
                            QLabel,      \
                            QTextEdit,   \
                            QGridLayout, \
                            QAction,     \
                            QFileDialog, \
                            QSizePolicy, \
                            QSlider
from PyQt5.QtGui import QImage,       \
                        QImageReader, \
                        QPixmap,      \
                        QIcon
from PyQt5.QtCore import Qt

import ImageTools

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        wid = QWidget()
        self.setCentralWidget(wid)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.gray)
        self.setPalette(palette)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        self.add_action(fileMenu, 'Open', 'Ctrl+O', 'Open new file', 
            self.showOpenDialog)
        self.add_action(fileMenu, 'Save as..', 'Ctrl+Shift+S', 'Save file as..', 
            self.showSaveDialog)
        self.add_action(fileMenu, 'Save', 'Ctrl+S', 'Save file', self.saveCurrent)

        self.pic = Picture(self)
        self.commands = Commands(self, self.pic)
  
        grid = QGridLayout()
        grid.addWidget(self.commands, 0, 0)
        grid.setSpacing(10)
        grid.addWidget(self.pic, 0, 1)

        wid.setLayout(grid)
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Insert Image Test')
        self.show()

    def add_action(self, fileMenu, name, shortcut, statustip, connection):
        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.setStatusTip(statustip)
        action.triggered.connect(connection)
        fileMenu.addAction(action)

    def showOpenDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 
        os.path.dirname(os.path.realpath(__file__)), '*png *jpg;; *.png;; *jpg')
        if fname[0]:
            self.pic.get_image(fname[0])
            self.pic.name = None
            self.commands.reset_sliders()

    def saveCurrent(self):
        if self.pic.name:
            self.pic.original.save(self.pic.name)
        else:
            self.showSaveDialog()

    def showSaveDialog(self):
        save_folder = self.pic.name or os.path.dirname(os.path.realpath(__file__))
        fname = QFileDialog.getSaveFileName(self, 'Save file as..', 
            save_folder, '*.png;; *jpg')
        if fname[0]:
            self.pic.name = fname[0]
            self.pic.original.save(self.pic.name)


class Commands(QWidget):
    def __init__(self, parent, pic):
        super().__init__(parent)
        self.parent = parent
        self.pic = pic
        self.sliders = []
        # self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, 
        #                           QSizePolicy.Preferred))
        self.make_color_sliders()

        grid = QGridLayout()
        for i, slider in enumerate(self.color_sliders.values()):
            grid.addWidget(slider, 0, i)

        self.setLayout(grid)

    def adjust_size(self):
        for slider in self.color_sliders.values():
            slider.resize(10, self.parent.height() // 3)

    def resizeEvent(self, event):
        self.adjust_size()

    def reset_sliders(self):
        for slider in self.sliders:
            # slider.setValue((abs(slider.maximum()) - abs(slider.minimum())) // 2)
            slider.setValue(0)

    def make_color_sliders(self):
        self.color_sliders = {}
        for color in 'r', 'g', 'b':
            self.color_sliders[color] = DirectionalSlider(Qt.Vertical)
            self.color_sliders[color].setFocusPolicy(Qt.NoFocus)
            self.color_sliders[color].resize(10, self.parent.height() // 3)
            self.color_sliders[color].setRange(0, 255)
            self.color_sliders[color].setValue(0)
            self.color_sliders[color].valueChanged.connect(
                partial(self.pic.changeColor, color, self.color_sliders[color])
            )
            self.sliders.append(self.color_sliders[color])


class DirectionalSlider(QSlider):
    def __init__(self, *args):
        super().__init__(*args)
        self._direction = 0
        self.previous_val = self.value()
        self.current_val = self.previous_val
        self.called = 0

    @property
    def direction(self):
        current_val = self.value()
        if current_val > self.previous_val:
            self._direction = 1
        elif current_val < self.previous_val:
            self._direction = -1
        else:
            self._direction = 0
        return self._direction



# class Slider(QSlider):
#     Nothing, Forward, Backward = range(3)
#     directionChanged = pyqtSignal(int)
#     def __init__(self, parent=None):
#         QSlider.__init__(self, parent)
#         self._direction = Slider.Nothing
#         self.last = self.value()/self.maximum()
#         self.valueChanged.connect(self.onValueChanged)

#     def onValueChanged(self, value):
#         current = value/self.maximum()
#         direction = Slider.Forward if self.last < current else Slider.Backward
#         if self._direction != direction:
#             self.directionChanged.emit(direction)
#             self._direction = direction
#         self.last = current

#     def direction(self):
#         return self._direction

# In the following part there is an example of the use of this class:

# class Widget(QWidget):
#     def __init__(self, parent=None):
#         QWidget.__init__(self, parent)
#         self.setLayout(QVBoxLayout())
#         slider = Slider(self)
#         slider.setOrientation(Qt.Horizontal)
#         self.layout().addWidget(slider)
#         slider.directionChanged.connect(self.onDirectionChanged)
#         slider.valueChanged.connect(self.onValueChanged)

#     def onDirectionChanged(self, direction):
#         if direction == Slider.Forward:
#             print("Forward")
#         elif direction == Slider.Backward:
#             print("Backward")

#     def onValueChanged(self, value):
#         dirstr = "Forward" if self.sender().direction() == Slider.Forward else "Backward"
#         print(value, dirstr)

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     w = Widget()
#     w.show()
#     sys.exit(app.exec_())




class Picture(QLabel):
    def __init__(self, parent):
        super().__init__('', parent)
        self.image = None
        self.name = None
        self.path = None
        self.parent = parent
        self.setMinimumSize(150, 150) # Minimum size of the displayed picture.
        # Vedi resizePolicy
        # self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, 
        #                                QSizePolicy.Expanding))

    def get_image(self, fname):
        self.prep_image(fname)

    def prep_image(self, fname):
        QImageReader.supportedImageFormats()
        self.original = ImageTools.prepare_image(fname, self)
        self.qt_tweaks()
        self.adjust_size()
        self.setPixmap()

    def changeColor(self, color, directional_slider):
        if self.image:
            self.original = ImageTools.change_color(self, color, 
                directional_slider)
            self.update()

    def adjust_size(self):
        w = self.parent.width()
        h = self.parent.height()
        image = QPixmap.fromImage(self.qim)
        self.image = image.scaled(3 * w // 4, h, Qt.KeepAspectRatio)

    def qt_tweaks(self):
        # This is the only way to avoid a Windows crash.
        r, g, b = self.original.split()
        image = ImageTools.merge("RGB", (b, g, r))
        data = ImageTools.get_data(image)
        self.qim = QImage(data, image.size[0], image.size[1],
            QImage.Format_ARGB32)

    def setPixmap(self):
        super().setPixmap(self.image)

    def update(self):
        self.qt_tweaks()
        self.adjust_size()
        self.setPixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image:
            self.adjust_size()
            self.setPixmap()
