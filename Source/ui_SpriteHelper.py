from PySide6.QtCore import (QLocale,
                            QSize, Qt)
from PySide6.QtGui import (QFont, QIcon)
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout,
                               QLayout, QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget, QMenuBar)

from SceneComposer import SpriteSelector, SceneComposerObjects


class Ui_MainWindow(object):
    def setupUi(self, MainWindow,SC:SceneComposerObjects):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.WindowModality.NonModal)
        MainWindow.resize(1266, 633)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(1266, 633))
        MainWindow.setSizeIncrement(QSize(0, 0))
        MainWindow.setBaseSize(QSize(1200, 600))
        font = QFont()
        font.setFamilies([u"Nimbus Sans Narrow [UKWN]"])
        font.setPointSize(11)
        font.setBold(False)
        font.setKerning(True)
        MainWindow.setFont(font)
        MainWindow.setAcceptDrops(False)
        icon = QIcon()
        icon.addFile(u":/icon/Icon-red.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAutoFillBackground(True)
        MainWindow.setLocale(QLocale(QLocale.English, QLocale.Europe))
        MainWindow.setAnimated(True)
        MainWindow.setDocumentMode(False)
        self.grid = QWidget(MainWindow)
        self.grid.setObjectName(u"grid")
        self.grid.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.grid.sizePolicy().hasHeightForWidth())
        self.grid.setSizePolicy(sizePolicy1)
        self.grid.setMinimumSize(QSize(0, 0))
        self.grid.setSizeIncrement(QSize(0, 0))
        self.grid.setBaseSize(QSize(0, 0))
        self.grid.setAutoFillBackground(False)

        self.Holder_Layout = QHBoxLayout(self.grid)

        self.ImageGrid_Layout = QVBoxLayout()
        self.ImageGrid_Layout.setSpacing(4)
        self.ImageGrid_Layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.ImageGrid_Layout.setObjectName(u"ImageGrid_Layout")
        self.ImageGrid_Layout.setContentsMargins(0, 0, 0, 0)

        self.menu = QMenuBar()
        self.ImageGrid_Layout.setMenuBar(self.menu)
        self.vSpacer = QSpacerItem(0, 15, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.ImageGrid_Layout.addItem(self.vSpacer)
        self.Holder_Layout.addLayout(self.ImageGrid_Layout)

        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(1)

        self.scrollArea = QScrollArea()
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")

        self.image_grid = QGridLayout(self.scrollAreaWidgetContents)
        self.image_grid.setSpacing(0)
        self.image_grid.setObjectName(u"image_grid")
        self.image_grid.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.image_grid.setContentsMargins(0, 0, 0, 0)

        self.ImageGrid_Layout.addWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.load_buttons_box = QVBoxLayout()
        self.load_buttons_box.setSpacing(0)
        self.load_buttons_box.setContentsMargins(0,0,0,0)
        self.load_buttons_box.setObjectName(u"load_buttons_box")
        self.load_buttons_box.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)

        self.sprite_selector = SpriteSelector(SC)
        self.sprite_selector.setMaximumWidth(220)

        self.load_buttons_box.addWidget(self.sprite_selector)

        self.Holder_Layout.addLayout(self.load_buttons_box)

        MainWindow.setCentralWidget(self.grid)