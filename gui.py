import os
from PyQt5.QtWidgets import QMainWindow, \
                            QWidget,     \
                            QLabel,      \
                            QTextEdit,   \
                            QGridLayout, \
                            QAction,     \
                            QFileDialog, \
                            QSizePolicy
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

        openFile = QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new file')
        openFile.triggered.connect(self.showOpenDialog)

        saveFile = QAction(QIcon('save.png'), 'Save as..', self)
        saveFile.setShortcut('Ctrl+Shift+S')
        saveFile.setStatusTip('Save file as..')
        saveFile.triggered.connect(self.showSaveDialog)

        saveCurrentFile = QAction('Save', self)
        saveCurrentFile.setShortcut('Ctrl+S')
        saveCurrentFile.setStatusTip('Save file')
        saveCurrentFile.triggered.connect(self.saveCurrent)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        fileMenu.addAction(saveCurrentFile)


        self.pic = Picture(self)
        text = QTextEdit()
        text.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, 
                                       QSizePolicy.Preferred))
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
        os.path.dirname(os.path.realpath(__file__)), '*png *jpg;; *.png;; *jpg')
        if fname[0]:
            self.pic.get_image(fname[0])
            self.pic.name = None

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

    def adjust_size(self):
        w = self.parent.width()
        h = self.parent.height()
        image = QPixmap.fromImage(self.qim)
        # self.image = image.scaledToWidth(3 * w // 4)
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

    def update(self, action):
        # Perform modifications on self.original with PIL.
        # Connect this function with the relevant Actions.
        self.qt_tweaks()
        self.adjust_size()
        self.setPixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image:
            self.adjust_size()
            self.setPixmap()
