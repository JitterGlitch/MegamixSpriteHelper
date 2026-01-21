# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ThumbnailWidgetDGaPff.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QLabel,
    QLayout, QPushButton, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_ThumbnailWidget(object):
    def setupUi(self, ThumbnailWidget):
        if not ThumbnailWidget.objectName():
            ThumbnailWidget.setObjectName(u"ThumbnailWidget")
        ThumbnailWidget.setEnabled(True)
        ThumbnailWidget.resize(365, 133)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ThumbnailWidget.sizePolicy().hasHeightForWidth())
        ThumbnailWidget.setSizePolicy(sizePolicy)
        ThumbnailWidget.setMinimumSize(QSize(365, 133))
        ThumbnailWidget.setMaximumSize(QSize(365, 133))
        ThumbnailWidget.setBaseSize(QSize(310, 133))
        self.horizontalLayout = QHBoxLayout(ThumbnailWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.thumbnail_h_layout = QHBoxLayout()
        self.thumbnail_h_layout.setObjectName(u"thumbnail_h_layout")
        self.thumbnail_image = QLabel(ThumbnailWidget)
        self.thumbnail_image.setObjectName(u"thumbnail_image")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.thumbnail_image.sizePolicy().hasHeightForWidth())
        self.thumbnail_image.setSizePolicy(sizePolicy1)
        self.thumbnail_image.setMinimumSize(QSize(128, 64))
        self.thumbnail_image.setMaximumSize(QSize(128, 64))
        self.thumbnail_image.setBaseSize(QSize(128, 64))

        self.thumbnail_h_layout.addWidget(self.thumbnail_image)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(ThumbnailWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy2)
        self.scrollArea.setMinimumSize(QSize(208, 37))
        self.scrollArea.setMaximumSize(QSize(208, 95))
        self.scrollArea.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 206, 92))
        self.formLayout = QFormLayout(self.scrollAreaWidgetContents)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.formLayout.setHorizontalSpacing(0)
        self.formLayout.setVerticalSpacing(0)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.thumbnail_v_layout = QVBoxLayout()
        self.thumbnail_v_layout.setObjectName(u"thumbnail_v_layout")
        self.remove_thumbnail_button = QPushButton(ThumbnailWidget)
        self.remove_thumbnail_button.setObjectName(u"remove_thumbnail_button")
        sizePolicy1.setHeightForWidth(self.remove_thumbnail_button.sizePolicy().hasHeightForWidth())
        self.remove_thumbnail_button.setSizePolicy(sizePolicy1)
        self.remove_thumbnail_button.setMinimumSize(QSize(206, 27))
        self.remove_thumbnail_button.setMaximumSize(QSize(206, 27))
        self.remove_thumbnail_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.thumbnail_v_layout.addWidget(self.remove_thumbnail_button)


        self.verticalLayout.addLayout(self.thumbnail_v_layout)


        self.thumbnail_h_layout.addLayout(self.verticalLayout)


        self.horizontalLayout.addLayout(self.thumbnail_h_layout)


        self.retranslateUi(ThumbnailWidget)

        QMetaObject.connectSlotsByName(ThumbnailWidget)
    # setupUi

    def retranslateUi(self, ThumbnailWidget):
        ThumbnailWidget.setWindowTitle(QCoreApplication.translate("ThumbnailWidget", u"Thumbnail Widget", None))
        self.thumbnail_image.setText("")
        self.remove_thumbnail_button.setText(QCoreApplication.translate("ThumbnailWidget", u"Remove Thumbnail", None))
    # retranslateUi

