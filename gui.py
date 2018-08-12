import os
import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, \
    QLabel, QTextEdit, QGridLayout, QAction, QFileDialog
from PyQt5.QtGui import QImage, QImageReader, QPixmap, QIcon
from PyQt5.QtCore import Qt

import ImageTools

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        wid = QWidget()
        self.setCentralWidget(wid)

        self.statusBar()

        openFile = QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new file')
        openFile.triggered.connect(self.showOpenDialog)

        saveFile = QAction(QIcon('save.png'), 'Save', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save file')
        saveFile.triggered.connect(self.showSaveDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)


        self.pic = Picture(self)
        text = QTextEdit()
        grid = QGridLayout()
        grid.addWidget(text, 0, 0)
        grid.setSpacing(10)
        grid.addWidget(self.pic, 0, 1)

        wid.setLayout(grid)
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Insert Image Test')
        self.show()

    def showOpenDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 
        os.path.dirname(os.path.realpath(__file__)), '*.png;; *jpg')
        if fname[0]:
            self.pic.get_image(fname[0])

    def showSaveDialog(self):
        fname = QFileDialog.getSaveFileName(self, 'Save file', 
        os.path.dirname(os.path.realpath(__file__)), '*.png;; *jpg')
        if fname[0]:
            self.pic.original_pic.save(fname[0])


class Picture(QLabel):
    def __init__(self, parent):
        super().__init__('', parent)
        self.image = None
        self.parent = parent

    def get_image(self, fname):
        self.prep_image(fname)

    def prep_image(self, fname):
        QImageReader.supportedImageFormats()
        self.original = ImageTools.prepare_image(fname, self)
        self.qt_tweaks()

    def adjust_size(self):
        w = self.parent.width()
        image = QPixmap.fromImage(self.qim)
        self.image = image.scaledToWidth(3 * w // 4)

    def qt_tweaks(self):
        data = ImageTools.get_data(self.original)
        self.qim = QImage(data, self.original.size[0], self.original.size[1],
            QImage.Format_ARGB32)
        self.adjust_size()
        self.setPixmap()

    def setPixmap(self):
        super().setPixmap(self.image)

    def update(self, action):
        # Perform modifications on self.original with PIL.
        # Connect this function with the relevant Actions.
        self.qt_tweaks()
        self.setPixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image:
            self.adjust_size()
            self.setPixmap()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())
