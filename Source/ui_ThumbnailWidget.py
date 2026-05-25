from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt)
from PySide6.QtWidgets import ( QFormLayout, QHBoxLayout, QLabel,
    QLayout, QPushButton, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget)

from widgets import OuterFrame


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
        ThumbnailWidget.setMinimumSize(QSize(395, 133))
        ThumbnailWidget.setMaximumSize(QSize(395, 133))
        ThumbnailWidget.setBaseSize(QSize(395, 133))

        self.scrollArea_contents = QWidget()
        self.scrollArea_contents.setContentsMargins(0,0,0,0)
        self.scrollArea_contents.setGeometry(QRect(0, 0, 395, 133))

        self.main_thumbnail_layout = QHBoxLayout(ThumbnailWidget)
        self.main_thumbnail_layout.setSpacing(0)
        self.main_thumbnail_layout.setContentsMargins(0, 0, 0, 0)
        self.thumbnail_info_layout = QHBoxLayout(self.scrollArea_contents)


        self.thumbnail_image = QLabel(ThumbnailWidget)

        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)

        self.thumbnail_image.setSizePolicy(sizePolicy1)
        self.thumbnail_image.setMinimumSize(QSize(128, 64))
        self.thumbnail_image.setMaximumSize(QSize(128, 64))
        self.thumbnail_image.setBaseSize(QSize(128, 64))


        self.outer_frame_scrollArea = OuterFrame(ThumbnailWidget)

        self.thumbnail_info_scrollArea = QScrollArea()

        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)

        self.thumbnail_info_scrollArea.setSizePolicy(sizePolicy2)

        self.thumbnail_info_scrollArea.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.thumbnail_info_scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.thumbnail_info_scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.thumbnail_info_scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 225, 92))

        self.thumbnail_info_scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.thumbnail_id_formLayout = QFormLayout(self.scrollAreaWidgetContents)
        self.thumbnail_id_formLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.thumbnail_id_formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.thumbnail_id_formLayout.setHorizontalSpacing(0)
        self.thumbnail_id_formLayout.setVerticalSpacing(0)
        self.thumbnail_id_formLayout.setContentsMargins(0, 0, 0, 0)



        self.remove_thumbnail_button = QPushButton(ThumbnailWidget)
        self.remove_thumbnail_button.setSizePolicy(sizePolicy1)
        self.remove_thumbnail_button.setMinimumSize(QSize(128, 27))
        self.remove_thumbnail_button.setMaximumSize(QSize(128, 27))
        self.remove_thumbnail_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)


        self.image_r_button_layout = QVBoxLayout()
        self.image_r_button_layout.addWidget(self.thumbnail_image)
        self.image_r_button_layout.addWidget(self.remove_thumbnail_button)

        self.thumbnail_info_layout.addLayout(self.image_r_button_layout)
        self.thumbnail_info_layout.addWidget(self.thumbnail_info_scrollArea)

        self.outer_frame_scrollArea.setSizePolicy(sizePolicy2)
        self.outer_frame_scrollArea.setMinimumSize(QSize(395, 133))
        self.outer_frame_scrollArea.setMaximumSize(QSize(395, 133))
        self.outer_frame_scrollArea.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.outer_frame_scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.outer_frame_scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.outer_frame_scrollArea.setWidgetResizable(True)


        self.outer_frame_scrollArea.setWidget(self.scrollArea_contents)




        #self.main_thumbnail_layout.addLayout(self.thumbnail_info_layout)


        self.retranslateUi(ThumbnailWidget)

        QMetaObject.connectSlotsByName(ThumbnailWidget)
    # setupUi

    def retranslateUi(self, ThumbnailWidget):
        ThumbnailWidget.setWindowTitle(QCoreApplication.translate("ThumbnailWidget", u"Thumbnail Widget", None))
        self.thumbnail_image.setText("")
        self.remove_thumbnail_button.setText(QCoreApplication.translate("ThumbnailWidget", u"Remove", None))
    # retranslateUi

