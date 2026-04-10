from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt, QRectF)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QCheckBox, QComboBox,
    QDoubleSpinBox, QGraphicsView, QHBoxLayout, QLabel,
    QLayout, QPushButton, QRadioButton, QScrollArea,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)
from superqt import QEnumComboBox

import FarcCreator


class Ui_SongFarcCreatorWindow(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"SongFarcCreatorWindow")
        Form.resize(629, 731)
        self.MainVLayout = QVBoxLayout(Form)
        self.MainVLayout.setObjectName(u"verticalLayout")
        self.MainVLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.song_info_settings_H_layout = QHBoxLayout()
        self.song_info_settings_H_layout.setObjectName(u"horizontalLayout_3")
        self.song_info_settings_H_layout.setContentsMargins(-1, -1, -1, 0)
        self.SongInfoLayout = QVBoxLayout()
        self.SongInfoLayout.setObjectName(u"SongInfoLayout")
        self.song_info_label = QLabel(Form)
        self.song_info_label.setObjectName(u"song_info_label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.song_info_label.sizePolicy().hasHeightForWidth())
        self.song_info_label.setSizePolicy(sizePolicy)
        self.song_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.SongInfoLayout.addWidget(self.song_info_label)

        self.song_id_label = QLabel(Form)
        self.song_id_label.setObjectName(u"song_id_label")

        self.SongInfoLayout.addWidget(self.song_id_label)

        self.farc_song_id_spinbox = QDoubleSpinBox(Form)
        self.farc_song_id_spinbox.setDecimals(0)
        self.farc_song_id_spinbox.setMinimum(1.000000000000000)
        self.farc_song_id_spinbox.setMaximum(4294967295.000000000000000)
        self.farc_song_id_spinbox.setValue(1.000000000000000)

        self.SongInfoLayout.addWidget(self.farc_song_id_spinbox)

        self.compression_label = QLabel(Form)
        self.compression_label.setObjectName(u"label_2")

        self.SongInfoLayout.addWidget(self.compression_label)

        self.compression_comboBox = QEnumComboBox(Form)
        self.compression_comboBox.setEnumClass(FarcCreator.Compression)
        self.compression_comboBox.setObjectName(u"comboBox")

        self.SongInfoLayout.addWidget(self.compression_comboBox)

        self.song_info_verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.SongInfoLayout.addItem(self.song_info_verticalSpacer)


        self.song_info_settings_H_layout.addLayout(self.SongInfoLayout)

        self.settings_layout = QVBoxLayout()
        self.settings_layout.setObjectName(u"settings_layout")
        self.settings_layout.setContentsMargins(-1, -1, -1, 0)
        self.settings_label = QLabel(Form)
        self.settings_label.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.settings_label.sizePolicy().hasHeightForWidth())
        self.settings_label.setSizePolicy(sizePolicy)
        self.settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.settings_layout.addWidget(self.settings_label)

        self.logo_checkbox = QCheckBox(Form)
        self.logo_checkbox.setText(u"Include Logo")
        self.logo_checkbox.setChecked(True)
        self.settings_layout.addWidget(self.logo_checkbox)

        self.ex_sprites_checkbox = QCheckBox(Form)
        self.ex_sprites_checkbox.setText(u"Include EX Sprites")

        self.settings_layout.addWidget(self.ex_sprites_checkbox)

        self.pv_back_sprite_checkbox = QCheckBox(Form)
        self.pv_back_sprite_checkbox.setText(u"Include PV_BACK sprite")

        self.settings_layout.addWidget(self.pv_back_sprite_checkbox)

        self.generate_spr_db_after_export_checkbox = QCheckBox(Form)
        self.generate_spr_db_after_export_checkbox.setText(u"Generate Spr_db after export")

        self.settings_layout.addWidget(self.generate_spr_db_after_export_checkbox)

        self.settings_verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.settings_layout.addItem(self.settings_verticalSpacer)


        self.song_info_settings_H_layout.addLayout(self.settings_layout)


        self.MainVLayout.addLayout(self.song_info_settings_H_layout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.scrollArea_2 = QScrollArea(Form)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scrollArea_2.sizePolicy().hasHeightForWidth())
        self.scrollArea_2.setSizePolicy(sizePolicy1)
        self.scrollArea_2.setMaximumSize(QSize(16777215, 50000))
        self.scrollArea_2.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 362, 210))
        self.pv_back_layout_choose_layout = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.pv_back_layout_choose_layout.setObjectName(u"pv_back_layout_choose_layout")
        self.label_3 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_3.setObjectName(u"label_3")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy2)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pv_back_layout_choose_layout.addWidget(self.label_3)


        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.horizontalLayout_2.addWidget(self.scrollArea_2)

        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setMaximumSize(QSize(16777215, 5000))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 361, 210))
        self.pv_back_scene_option_layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.pv_back_scene_option_layout.setObjectName(u"pv_back_scene_option_layout")
        self.label_4 = QLabel(self.scrollAreaWidgetContents)
        self.label_4.setObjectName(u"label_4")
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pv_back_scene_option_layout.addWidget(self.label_4)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_2.addWidget(self.scrollArea)


        self.MainVLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)

        self.MainVLayout.addLayout(self.horizontalLayout)

        self.export_farc_pushbutton = QPushButton(Form)
        self.export_farc_pushbutton.setObjectName(u"pushButton")

        self.MainVLayout.addWidget(self.export_farc_pushbutton)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Song Farc Creator", u"Song Farc Creator", None))
        self.song_info_label.setText(QCoreApplication.translate("Form", u"Basic ass info", None))
        self.song_id_label.setText(QCoreApplication.translate("Form", u"Song ID:", None))
        self.compression_label.setText(QCoreApplication.translate("Form", u"Compression", None))
        self.settings_label.setText(QCoreApplication.translate("Form", u"Settings", None))

        self.label_3.setText(QCoreApplication.translate("Form", u"Select Layout:", None))

        self.label_4.setText(QCoreApplication.translate("Form", u"Scene Options", None))

        self.export_farc_pushbutton.setText(QCoreApplication.translate("Form", u"Export Song Sprite Farc", None))
    # retranslateUi

