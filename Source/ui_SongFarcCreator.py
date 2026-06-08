from PySide6.QtCore import (QCoreApplication,
                            QMetaObject, QRect,
                            QSize, Qt)
from PySide6.QtGui import QIcon

from PySide6.QtWidgets import (QAbstractScrollArea, QCheckBox,
                               QDoubleSpinBox, QHBoxLayout, QLabel,
                               QLayout, QPushButton, QScrollArea,
                               QSizePolicy, QSpacerItem, QVBoxLayout, QWidget, QTabWidget, QFrame)
from superqt import QEnumComboBox

import FarcCreator
from SceneComposer import SpriteGroup
from widgets import SpriteGroupPreview


class Ui_SongFarcCreatorWindow(object):
    def setupUi(self, Form, SC_obj,sprite_group_enum):
        if not Form.objectName():
            Form.setObjectName(u"SongFarcCreatorWindow")
        #Form.resize(629, 731)

        icon = QIcon()
        icon.addFile(u":/icon/Icon-red.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        Form.setWindowIcon(icon)

        self.MainVLayout = QVBoxLayout(Form)
        self.MainVLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)

        self.song_info_settings_H_layout = QHBoxLayout()
        self.song_info_settings_H_layout.setContentsMargins(-1, -1, -1, 0)

        self.SongInfoLayout = QVBoxLayout()

        self.song_info_label = QLabel(Form)

        header_font = self.song_info_label.font()
        header_font.setBold(True)


        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.song_info_label.sizePolicy().hasHeightForWidth())

        self.song_info_label.setSizePolicy(sizePolicy)
        self.song_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.SongInfoLayout.addWidget(self.song_info_label)

        self.song_id_label = QLabel(Form)

        self.SongInfoLayout.addWidget(self.song_id_label)

        self.farc_song_id_spinbox = QDoubleSpinBox(Form)
        self.farc_song_id_spinbox.setDecimals(0)
        self.farc_song_id_spinbox.setMinimum(1.000000000000000)
        self.farc_song_id_spinbox.setMaximum(4294967295.000000000000000)
        self.farc_song_id_spinbox.setValue(1.000000000000000)

        self.SongInfoLayout.addWidget(self.farc_song_id_spinbox)

        self.compression_label = QLabel(Form)

        self.SongInfoLayout.addWidget(self.compression_label)

        self.compression_comboBox = QEnumComboBox(Form)
        self.compression_comboBox.setEnumClass(FarcCreator.Compression)

        self.SongInfoLayout.addWidget(self.compression_comboBox)

        self.song_info_verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.SongInfoLayout.addItem(self.song_info_verticalSpacer)


        self.song_info_settings_H_layout.addLayout(self.SongInfoLayout)

        self.settings_layout = QVBoxLayout()
        self.settings_layout.setContentsMargins(-1, -1, -1, 0)
        self.settings_label = QLabel(Form)
        sizePolicy.setHeightForWidth(self.settings_label.sizePolicy().hasHeightForWidth())
        self.settings_label.setSizePolicy(sizePolicy)
        self.settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.settings_layout.addWidget(self.settings_label)

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

        self.sprite_group_chooser_layout = QVBoxLayout()
        self.sprite_group_chooser_layout.setContentsMargins(-1, -1, -1, 0)



        #self.sprite_group_V_spacer = QSpacerItem(0,20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)


        self.default_sprite_group_widget = SpriteGroupPreview("Default Sprite Group",SC_obj=SC_obj,sprite_group=sprite_group_enum)
        self.ex_sprite_group_widget = SpriteGroupPreview("_EX Sprite Group",SC_obj=SC_obj,sprite_group=sprite_group_enum)
        self.pv_back_sprite_group_widget = SpriteGroupPreview("PV_BACK Sprite Group",SC_obj=SC_obj,sprite_group=sprite_group_enum)


        self.sprite_group_chooser_layout.addWidget(self.default_sprite_group_widget)
        self.sprite_group_chooser_layout.addWidget(self.ex_sprite_group_widget)
        self.sprite_group_chooser_layout.addWidget(self.pv_back_sprite_group_widget)


        self.pv_back_options_layout = QHBoxLayout()
        self.pv_back_options_layout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.pv_back_options_layout.setContentsMargins(-1, -1, -1, 0)

        self.pv_back_scene_options_scrollArea = QScrollArea(Form)

        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pv_back_scene_options_scrollArea.sizePolicy().hasHeightForWidth())

        self.pv_back_scene_options_scrollArea.setSizePolicy(sizePolicy1)
        self.pv_back_scene_options_scrollArea.setMinimumHeight(160)
        self.pv_back_scene_options_scrollArea.setMaximumSize(QSize(16777215, 50000))
        self.pv_back_scene_options_scrollArea.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.pv_back_scene_options_scrollArea.setWidgetResizable(True)

        self.select_layout_scrollAreaContents = QWidget()
        self.select_layout_scrollAreaContents.setGeometry(QRect(0, 0, 362, 210))

        self.pv_back_layout_choose_layout = QVBoxLayout(self.select_layout_scrollAreaContents)

        self.select_layout_label = QLabel()


        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.select_layout_label.sizePolicy().hasHeightForWidth())

        self.select_layout_label.setSizePolicy(sizePolicy2)
        self.select_layout_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pv_back_layout_choose_layout.addWidget(self.select_layout_label)


        self.pv_back_scene_options_scrollArea.setWidget(self.select_layout_scrollAreaContents)


        self.pv_back_select_layout = QVBoxLayout()
        self.pv_back_select_layout.addWidget(self.select_layout_label)
        self.pv_back_select_layout.addWidget(self.pv_back_scene_options_scrollArea)

        self.pv_back_options_layout.addLayout(self.pv_back_select_layout)


        self.select_layout_scrollArea = QScrollArea(Form)
        self.select_layout_scrollArea.setMaximumSize(QSize(16777215, 5000))
        self.select_layout_scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 362, 210))

        self.select_layout_scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.pv_back_scene_option_layout = QVBoxLayout(self.scrollAreaWidgetContents)

        self.scene_options_label = QLabel()

        sizePolicy.setHeightForWidth(self.scene_options_label.sizePolicy().hasHeightForWidth())

        self.scene_options_label.setSizePolicy(sizePolicy)
        self.scene_options_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pv_back_scene_option_Vlayout = QVBoxLayout()
        self.pv_back_scene_option_Vlayout.addWidget(self.scene_options_label)
        self.pv_back_scene_option_Vlayout.addWidget(self.select_layout_scrollArea)


        self.pv_back_options_layout.addLayout(self.pv_back_scene_option_Vlayout)






        #self.MainVLayout.addLayout(self.pv_back_options_layout)

        self.pv_back_preview_layout = QHBoxLayout()
        self.pv_back_preview_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.pv_back_preview_layout.setContentsMargins(-1, -1, -1, 0)

        #self.MainVLayout.addLayout(self.pv_back_preview_layout)
        self.sprite_group_tab = QFrame()
        self.sprite_group_tab.setLayout(self.sprite_group_chooser_layout)

        self.pv_back_combined_layout = QVBoxLayout()
        self.pv_back_combined_layout.addLayout(self.pv_back_options_layout)
        self.pv_back_combined_layout.addLayout(self.pv_back_preview_layout)

        self.pv_back_tab = QFrame()
        self.pv_back_tab.setLayout(self.pv_back_combined_layout)

        self.tab_view = QTabWidget()
        self.tab_view.addTab(self.sprite_group_tab,"Sprite Groups")
        self.tab_view.addTab(self.pv_back_tab,"PV_BACK")

        self.MainVLayout.addWidget(self.tab_view)

        self.export_farc_pushbutton = QPushButton(Form)
        self.MainVLayout.addWidget(self.export_farc_pushbutton)


        self.song_info_label.setFont(header_font)
        self.select_layout_label.setFont(header_font)
        self.scene_options_label.setFont(header_font)
        self.settings_label.setFont(header_font)

        self.retranslateUi(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Song Farc Creator", u"Song Farc Creator", None))
        self.song_info_label.setText(QCoreApplication.translate("Form", u"Basic Song Info", None))
        self.song_id_label.setText(QCoreApplication.translate("Form", u"Song ID:", None))
        self.compression_label.setText(QCoreApplication.translate("Form", u"Compression", None))
        self.settings_label.setText(QCoreApplication.translate("Form", u"Settings", None))

        self.select_layout_label.setText(QCoreApplication.translate("Form", u"Select Layout:", None))

        self.scene_options_label.setText(QCoreApplication.translate("Form", u"Scene Options", None))

        self.export_farc_pushbutton.setText(QCoreApplication.translate("Form", u"Export Song Sprite Farc", None))

