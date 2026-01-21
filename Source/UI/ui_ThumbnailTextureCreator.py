# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Thumbnail Texture CreatorsQXeDJ.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
                            QSize, Qt)
from PySide6.QtGui import (QIcon)
from PySide6.QtWidgets import (QAbstractScrollArea, QGridLayout,
                               QLabel, QPushButton, QScrollArea,
                               QVBoxLayout, QWidget, QHBoxLayout)
from superqt import QEnumComboBox

from Source.FarcCreator import Compression
from Source.UI.widgets import SongpackNameInput


class Ui_ThumbnailTextureCreator(object):
    def setupUi(self, ThumbnailTextureCreator):
        if not ThumbnailTextureCreator.objectName():
            ThumbnailTextureCreator.setObjectName(u"ThumbnailTextureCreator")
        ThumbnailTextureCreator.resize(742, 600)
        ThumbnailTextureCreator.setMinimumSize(QSize(742, 600))
        icon = QIcon()
        icon.addFile(u":/icon/Icon-red.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        ThumbnailTextureCreator.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(ThumbnailTextureCreator)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(-1, 0, -1, -1)

        self.thumbnails_to_fillout_label = QLabel(ThumbnailTextureCreator)
        self.thumbnails_to_fillout_label.setObjectName(u"thumbnails_to_fillout_label")
        self.thumbnails_to_fillout_label.setMinimumSize(QSize(330, 0))

        self.gridLayout_2.addWidget(self.thumbnails_to_fillout_label, 1, 1, 1, 1)

        self.thumbnails_loaded_label = QLabel(ThumbnailTextureCreator)
        self.thumbnails_loaded_label.setObjectName(u"thumbnails_loaded_label")

        self.gridLayout_2.addWidget(self.thumbnails_loaded_label, 0, 1, 1, 1)

        self.load_folder_button = QPushButton(ThumbnailTextureCreator)
        self.load_folder_button.setObjectName(u"load_folder_button")

        self.gridLayout_2.addWidget(self.load_folder_button, 0, 0, 1, 1)

        self.load_image_button = QPushButton(ThumbnailTextureCreator)
        self.load_image_button.setObjectName(u"load_image_button")

        self.gridLayout_2.addWidget(self.load_image_button, 1, 0, 1, 1)

        # self.mod_name_lineedit = QLineEdit(ThumbnailTextureCreator)
        # self.mod_name_lineedit.setObjectName(u"mod_name_lineedit")
        # self.mod_name_lineedit.setMaxLength(200)
        # self.mod_name_lineedit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mod_name_lineedit = SongpackNameInput()

        self.gridLayout_2.addWidget(self.mod_name_lineedit, 2, 0, 1, 1)

        self.export_farc_button = QPushButton(ThumbnailTextureCreator)
        self.export_farc_button.setObjectName(u"export_farc_button")

        self.gridLayout_2.addWidget(self.export_farc_button, 3, 0, 1, 1)

        self.delete_all_thumbs_button = QPushButton(ThumbnailTextureCreator)
        self.delete_all_thumbs_button.setObjectName(u"delete_all_thumbs_button")

        self.gridLayout_2.addWidget(self.delete_all_thumbs_button, 2, 1, 1, 1)

        self.H_Layout = QHBoxLayout()
        self.farc_compression_label = QLabel()
        self.farc_compression_label.setText("Compression:")
        self.farc_compression_label.setMaximumSize(QSize(110,33))

        self.H_Layout.addWidget(self.farc_compression_label)
        #self.gridLayout_2.addWidget(self.farc_compression_label, 3, 1 ,1 ,1)

        self.farc_compression_combobox = QEnumComboBox()
        self.farc_compression_combobox.setEnumClass(Compression)
        self.H_Layout.addWidget(self.farc_compression_combobox)

        self.gridLayout_2.addItem(self.H_Layout, 3, 1, 1, 1)


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


        self.retranslateUi(ThumbnailTextureCreator)

        QMetaObject.connectSlotsByName(ThumbnailTextureCreator)
    # setupUi

    def retranslateUi(self, ThumbnailTextureCreator):
        ThumbnailTextureCreator.setWindowTitle(QCoreApplication.translate("ThumbnailTextureCreator", u"Thumbnail Texture Creator", None))
        self.thumbnails_to_fillout_label.setText(QCoreApplication.translate("ThumbnailTextureCreator", u"ID's left to fill out: 0", None))
        self.thumbnails_loaded_label.setText(QCoreApplication.translate("ThumbnailTextureCreator", u"Unique Thumbnails loaded: 0", None))
        self.load_folder_button.setText(QCoreApplication.translate("ThumbnailTextureCreator", u"Load from folder", None))
        self.load_image_button.setText(QCoreApplication.translate("ThumbnailTextureCreator", u"Load image", None))
        self.export_farc_button.setText(QCoreApplication.translate("ThumbnailTextureCreator", u"Export Farc", None))
        self.delete_all_thumbs_button.setText(QCoreApplication.translate("ThumbnailTextureCreator", u"Delete all thumbnails", None))
    # retranslateUi

