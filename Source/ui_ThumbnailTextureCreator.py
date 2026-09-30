from PySide6.QtCore import (QRect,QSize, Qt)
from PySide6.QtGui import (QIcon)
from PySide6.QtWidgets import (QAbstractScrollArea, QGridLayout,
                               QLabel, QPushButton, QScrollArea,
                               QVBoxLayout, QWidget, QHBoxLayout, QCheckBox)
from superqt import QEnumComboBox

from FarcCreator import Compression
from SceneComposer import SpriteStatusDisplay, SpriteStatus, SongpackNameInput


class Ui_ThumbnailTextureCreator(object):
    def setupUi(self, ThumbnailTextureCreator):
        if not ThumbnailTextureCreator.objectName():
            ThumbnailTextureCreator.setObjectName(u"ThumbnailTextureCreator")
        ThumbnailTextureCreator.resize(850, 600)
        ThumbnailTextureCreator.setMinimumSize(QSize(850, 600))
        icon = QIcon()
        icon.addFile(u":/icon/Icon-red.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        ThumbnailTextureCreator.setWindowIcon(icon)
        ThumbnailTextureCreator.setWindowTitle( u"Thumbnail Texture Creator")

        self.verticalLayout = QVBoxLayout(ThumbnailTextureCreator)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)

        self.thumbnails_to_fillout_label = QLabel(ThumbnailTextureCreator)
        self.thumbnails_to_fillout_label.setObjectName(u"thumbnails_to_fillout_label")
        self.thumbnails_to_fillout_label.setMinimumSize(QSize(330, 0))
        self.thumbnails_to_fillout_label.setText( u"ID's left to fill out: 0")


        self.ignore_warnings_checkbox = QCheckBox(ThumbnailTextureCreator)
        self.ignore_warnings_checkbox.setText("Ignore warnings")
        self.ignore_warnings_checkbox.setChecked(False)

        self.thumbnail_status_display = SpriteStatusDisplay()
        self.thumbnail_status_display.set_status(SpriteStatus.PLEASE_WAIT,"No Thumbnails loaded")

        self.warning_layout = QHBoxLayout()
        self.warning_layout.addWidget(self.thumbnail_status_display)
        self.warning_layout.addWidget(self.ignore_warnings_checkbox)

        self.load_folder_button = QPushButton(ThumbnailTextureCreator)
        self.load_folder_button.setObjectName(u"load_folder_button")
        self.load_folder_button.setText(u"Load from folder")


        self.load_image_button = QPushButton(ThumbnailTextureCreator)
        self.load_image_button.setObjectName(u"load_image_button")
        self.load_image_button.setText( u"Load image")


        self.mod_name_lineedit = SongpackNameInput()

        self.export_farc_button = QPushButton(ThumbnailTextureCreator)
        self.export_farc_button.setObjectName(u"export_farc_button")
        self.export_farc_button.setText( u"Export Farc")


        self.delete_all_thumbs_button = QPushButton(ThumbnailTextureCreator)
        self.delete_all_thumbs_button.setObjectName(u"delete_all_thumbs_button")
        self.delete_all_thumbs_button.setText(u"Remove all thumbnails")


        self.H_Layout = QHBoxLayout()
        self.farc_compression_label = QLabel()
        self.farc_compression_label.setText("Compression:")
        self.farc_compression_label.setMaximumSize(QSize(110,33))

        self.H_Layout.addWidget(self.farc_compression_label)

        self.farc_compression_combobox = QEnumComboBox()
        self.farc_compression_combobox.setEnumClass(Compression)
        self.H_Layout.addWidget(self.farc_compression_combobox)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(-1, 0, -1, -1)

        self.gridLayout_2.addWidget(self.load_folder_button,         0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.load_image_button,          1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.delete_all_thumbs_button,   2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.thumbnails_to_fillout_label,3, 0, 1, 1)

        self.gridLayout_2.addWidget(self.mod_name_lineedit,          0, 1, 1, 1)
        self.gridLayout_2.addItem(self.H_Layout,                     1, 1, 1, 1)
        self.gridLayout_2.addLayout(self.warning_layout,             2, 1, 1, 1)
        self.gridLayout_2.addWidget(self.export_farc_button,         3, 1, 1, 1)

        self.verticalLayout.addLayout(self.gridLayout_2)

        self.scrollArea = QScrollArea(ThumbnailTextureCreator)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setAcceptDrops(False)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 730, 455))
        self.scrollAreaWidgetContents.setMinimumSize(QSize(0, 0))
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

