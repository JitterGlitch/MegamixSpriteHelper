from PySide6.QtCore import (QCoreApplication, QLocale,
                            QMetaObject, QRect,
                            QSize, Qt)
from PySide6.QtGui import (QFont, QIcon,
                           QPainter)
from PySide6.QtWidgets import (QAbstractScrollArea, QCheckBox, QComboBox,
                               QDoubleSpinBox, QFrame, QGridLayout, QHBoxLayout,
                               QLabel, QLayout, QPushButton,
                               QScrollArea, QSizePolicy, QSpacerItem, QStackedWidget,
                               QTabWidget, QVBoxLayout, QWidget)
from superqt import QEnumComboBox
from Source.FarcCreator import Compression

from Source.SceneComposer import QScalingGraphicsScene
import Source.resources

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
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
        MainWindow.setWindowTitle(u"Megamix Sprite Helper 1.1.1")
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
        self.horizontalLayout_5 = QHBoxLayout(self.grid)
        self.horizontalLayout_5.setSpacing(5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(5, 5, 5, 5)
        self.image_grid = QGridLayout()
        self.image_grid.setSpacing(5)
        self.image_grid.setObjectName(u"image_grid")
        self.image_grid.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.image_grid.setContentsMargins(0, 0, 0, 0)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(1)

        self.graphics_scene_view = QScalingGraphicsScene()
        self.graphics_scene_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_scene_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_scene_view.setSizePolicy(sizePolicy2)
        self.graphics_scene_view.setMinimumSize(QSize(256, 144))
        self.graphics_scene_view.setMaximumSize(QSize(1920, 1080))
        self.graphics_scene_view.setSizeIncrement(QSize(0, 0))
        self.graphics_scene_view.setBaseSize(QSize(640, 360))
        self.graphics_scene_view.setRenderHint(QPainter.Antialiasing, True)
        self.graphics_scene_view.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.graphics_scene_view.setBackgroundBrush(Qt.black)
        self.image_grid.addWidget(self.graphics_scene_view,1,0,1,1)

        self.graphics_scene_view1 = QScalingGraphicsScene()
        self.graphics_scene_view1.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_scene_view1.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_scene_view1.setSizePolicy(sizePolicy2)
        self.graphics_scene_view1.setMinimumSize(QSize(256, 144))
        self.graphics_scene_view1.setMaximumSize(QSize(1920, 1080))
        self.graphics_scene_view1.setSizeIncrement(QSize(0, 0))
        self.graphics_scene_view1.setBaseSize(QSize(640, 360))
        self.graphics_scene_view1.setRenderHint(QPainter.Antialiasing, True)
        self.graphics_scene_view1.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.graphics_scene_view1.setBackgroundBrush(Qt.black)

        self.image_grid.addWidget(self.graphics_scene_view1, 0, 0, 1, 1)

        self.graphics_scene_view2 = QScalingGraphicsScene()
        self.graphics_scene_view2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_scene_view2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_scene_view2.setSizePolicy(sizePolicy2)
        self.graphics_scene_view2.setMinimumSize(QSize(256, 144))
        self.graphics_scene_view2.setMaximumSize(QSize(1920, 1080))
        self.graphics_scene_view2.setSizeIncrement(QSize(0, 0))
        self.graphics_scene_view2.setBaseSize(QSize(640, 360))
        self.graphics_scene_view2.setRenderHint(QPainter.Antialiasing, True)
        self.graphics_scene_view2.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.graphics_scene_view2.setBackgroundBrush(Qt.black)

        self.image_grid.addWidget(self.graphics_scene_view2, 1, 1, 1, 1)

        self.graphics_scene_view3 = QScalingGraphicsScene()
        self.graphics_scene_view3.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_scene_view3.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_scene_view3.setSizePolicy(sizePolicy2)
        self.graphics_scene_view3.setMinimumSize(QSize(256, 144))
        self.graphics_scene_view3.setMaximumSize(QSize(1920, 1080))
        self.graphics_scene_view3.setSizeIncrement(QSize(0, 0))
        self.graphics_scene_view3.setBaseSize(QSize(640, 360))
        self.graphics_scene_view3.setRenderHint(QPainter.Antialiasing, True)
        self.graphics_scene_view3.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.graphics_scene_view3.setBackgroundBrush(Qt.black)

        self.image_grid.addWidget(self.graphics_scene_view3, 0, 1, 1, 1)


        self.horizontalLayout_5.addLayout(self.image_grid)

        self.load_buttons_box = QVBoxLayout()
        self.load_buttons_box.setSpacing(5)
        self.load_buttons_box.setObjectName(u"load_buttons_box")
        self.load_buttons_box.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")


        self.load_buttons_box_row3 = QHBoxLayout()
        self.load_buttons_box_row3.setSpacing(5)
        self.load_buttons_box_row3.setObjectName(u"load_buttons_box_row3")
        self.load_buttons_box_row3.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.load_buttons_box_row3.setContentsMargins(-1, 0, -1, -1)
        self.has_logo_checkbox = QCheckBox(self.grid)
        self.has_logo_checkbox.setObjectName(u"has_logo_checkbox")
        self.has_logo_checkbox.setCheckable(True)
        self.has_logo_checkbox.setChecked(True)

        self.load_buttons_box_row3.addWidget(self.has_logo_checkbox)

        self.new_classics_checkbox = QCheckBox(self.grid)
        self.new_classics_checkbox.setObjectName(u"new_classics_checkbox")
        self.new_classics_checkbox.setChecked(True)

        self.load_buttons_box_row3.addWidget(self.new_classics_checkbox)




        self.current_sprite_combobox = QComboBox(self.grid)
        self.current_sprite_combobox.addItem("")
        self.current_sprite_combobox.addItem("")
        self.current_sprite_combobox.addItem("")
        self.current_sprite_combobox.addItem("")
        self.current_sprite_combobox.setObjectName(u"current_sprite_combobox")

        self.load_buttons_box.addWidget(self.current_sprite_combobox)

        self.sprite_options_v_layout = QVBoxLayout()
        self.sprite_options_v_layout.setContentsMargins(-1, 0, -1, -1)
        self.load_image_button = QPushButton(self.grid)
        self.load_image_button.setText("Load Image")
        self.sprite_options_v_layout.addWidget(self.load_image_button)
        self.load_buttons_box.addLayout(self.sprite_options_v_layout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.flip_horizontal_button = QPushButton(self.grid)
        self.flip_horizontal_button.setObjectName(u"flip_horizontal_button")

        self.horizontalLayout_2.addWidget(self.flip_horizontal_button)

        self.flip_vertical_button = QPushButton(self.grid)
        self.flip_vertical_button.setObjectName(u"flip_vertical_button")

        self.horizontalLayout_2.addWidget(self.flip_vertical_button)
        #self.sprite_options_v_layout.addLayout(self.horizontalLayout_2)


        self.load_buttons_box.addLayout(self.horizontalLayout_2)

        self.image_edit_scroll_area = QScrollArea(self.grid)
        self.image_edit_scroll_area.setObjectName(u"image_edit_scroll_area")
        self.image_edit_scroll_area.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.image_edit_scroll_area.sizePolicy().hasHeightForWidth())
        self.image_edit_scroll_area.setSizePolicy(sizePolicy3)
        self.image_edit_scroll_area.setMinimumSize(QSize(0, 229))
        self.image_edit_scroll_area.setAutoFillBackground(False)
        self.image_edit_scroll_area.setFrameShape(QFrame.Shape.StyledPanel)
        self.image_edit_scroll_area.setFrameShadow(QFrame.Shadow.Sunken)
        self.image_edit_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.image_edit_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.image_edit_scroll_area.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.image_edit_scroll_area.setWidgetResizable(True)
        self.image_edit_scroll_area.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft)
        self.image_edit_area_widget_properties = QWidget()
        self.image_edit_area_widget_properties.setObjectName(u"image_edit_area_widget_properties")
        self.image_edit_area_widget_properties.setGeometry(QRect(0, 0, 196, 227))
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.image_edit_area_widget_properties.sizePolicy().hasHeightForWidth())
        self.image_edit_area_widget_properties.setSizePolicy(sizePolicy4)
        self.image_edit_area_widget_properties.setMinimumSize(QSize(0, 220))
        self.image_edit_area_widget_properties.setMaximumSize(QSize(16777215, 16777215))
        self.image_edit_area_widget_properties.setSizeIncrement(QSize(0, -31072))
        self.image_edit_area_widget_properties.setBaseSize(QSize(0, -31072))
        self.image_edit_area_widget_properties.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.image_edit_area_widget_properties.setAutoFillBackground(True)
        self.verticalLayout = QVBoxLayout(self.image_edit_area_widget_properties)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.sprite_controls = QStackedWidget(self.image_edit_area_widget_properties)
        self.sprite_controls.setObjectName(u"sprite_controls")
        sizePolicy3.setHeightForWidth(self.sprite_controls.sizePolicy().hasHeightForWidth())
        self.sprite_controls.setSizePolicy(sizePolicy3)
        self.sprite_controls.setMaximumSize(QSize(16777215, 25000))
        self.jacket_tab = QWidget()
        self.jacket_tab.setObjectName(u"jacket_tab")
        self.verticalLayout_5 = QVBoxLayout(self.jacket_tab)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.jacket_tab_scrollarea = QScrollArea(self.jacket_tab)
        self.jacket_tab_scrollarea.setObjectName(u"jacket_tab_scrollarea")
        self.jacket_tab_scrollarea.setWidgetResizable(True)
        self.jacket_scrollarea_contents = QWidget()
        self.jacket_scrollarea_contents.setObjectName(u"jacket_scrollarea_contents")
        self.jacket_scrollarea_contents.setGeometry(QRect(0, 0, 176, 213))
        self.verticalLayout_10 = QVBoxLayout(self.jacket_scrollarea_contents)
        self.verticalLayout_10.setSpacing(2)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.jacket_tab_scrollarea.setWidget(self.jacket_scrollarea_contents)

        self.verticalLayout_5.addWidget(self.jacket_tab_scrollarea)

        self.sprite_controls.addWidget(self.jacket_tab)
        self.background_tab = QWidget()
        self.background_tab.setObjectName(u"background_tab")
        self.verticalLayout_2 = QVBoxLayout(self.background_tab)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.background_tab_scrollarea = QScrollArea(self.background_tab)
        self.background_tab_scrollarea.setObjectName(u"background_tab_scrollarea")
        self.background_tab_scrollarea.setWidgetResizable(True)
        self.background_scrollarea_contents = QWidget()
        self.background_scrollarea_contents.setObjectName(u"background_scrollarea_contents")
        self.background_scrollarea_contents.setGeometry(QRect(0, 0, 194, 225))
        self.verticalLayout_8 = QVBoxLayout(self.background_scrollarea_contents)
        self.verticalLayout_8.setSpacing(2)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.background_tab_scrollarea.setWidget(self.background_scrollarea_contents)

        self.verticalLayout_2.addWidget(self.background_tab_scrollarea)

        self.sprite_controls.addWidget(self.background_tab)
        self.thumbnail_tab = QWidget()
        self.thumbnail_tab.setObjectName(u"thumbnail_tab")
        self.verticalLayout_7 = QVBoxLayout(self.thumbnail_tab)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.thumbnail_tab_scrollarea = QScrollArea(self.thumbnail_tab)
        self.thumbnail_tab_scrollarea.setObjectName(u"thumbnail_tab_scrollarea")
        self.thumbnail_tab_scrollarea.setWidgetResizable(True)
        self.thumbnail_scrollarea_contents = QWidget()
        self.thumbnail_scrollarea_contents.setObjectName(u"thumbnail_scrollarea_contents")
        self.thumbnail_scrollarea_contents.setGeometry(QRect(0, 0, 176, 213))
        self.verticalLayout_12 = QVBoxLayout(self.thumbnail_scrollarea_contents)
        self.verticalLayout_12.setSpacing(2)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.thumbnail_tab_scrollarea.setWidget(self.thumbnail_scrollarea_contents)

        self.verticalLayout_7.addWidget(self.thumbnail_tab_scrollarea)

        self.sprite_controls.addWidget(self.thumbnail_tab)
        self.logo_tab = QWidget()
        self.logo_tab.setObjectName(u"logo_tab")
        self.verticalLayout_6 = QVBoxLayout(self.logo_tab)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.logo_tab_scrollarea = QScrollArea(self.logo_tab)
        self.logo_tab_scrollarea.setObjectName(u"logo_tab_scrollarea")
        self.logo_tab_scrollarea.setWidgetResizable(True)
        self.logo_scrollarea_contents = QWidget()
        self.logo_scrollarea_contents.setObjectName(u"logo_scrollarea_contents")
        self.logo_scrollarea_contents.setGeometry(QRect(0, 0, 176, 213))
        self.verticalLayout_11 = QVBoxLayout(self.logo_scrollarea_contents)
        self.verticalLayout_11.setSpacing(2)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.logo_tab_scrollarea.setWidget(self.logo_scrollarea_contents)

        self.verticalLayout_6.addWidget(self.logo_tab_scrollarea)

        self.sprite_controls.addWidget(self.logo_tab)

        self.verticalLayout.addWidget(self.sprite_controls)

        self.image_edit_scroll_area.setWidget(self.image_edit_area_widget_properties)

        self.load_buttons_box.addWidget(self.image_edit_scroll_area)
        self.load_buttons_box.addLayout(self.load_buttons_box_row3)

        self.image_tab_vertical_layout = QVBoxLayout()
        self.image_tab_vertical_layout.setSpacing(5)
        self.image_tab_vertical_layout.setObjectName(u"image_tab_vertical_layout")
        self.export_controls = QTabWidget(self.grid)
        self.export_controls.setObjectName(u"export_controls")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.export_controls.sizePolicy().hasHeightForWidth())
        self.export_controls.setSizePolicy(sizePolicy5)
        self.export_controls.setTabPosition(QTabWidget.TabPosition.North)
        self.export_controls.setIconSize(QSize(16, 16))
        self.export_controls.setElideMode(Qt.TextElideMode.ElideNone)
        self.export_controls.setDocumentMode(False)
        self.to_farc_tab = QWidget()
        self.to_farc_tab.setObjectName(u"to_farc_tab")
        self.verticalLayout_3 = QVBoxLayout(self.to_farc_tab)
        self.verticalLayout_3.setSpacing(4)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(4, 4, 4, 4)
        self.song_id_label = QLabel(self.to_farc_tab)
        self.song_id_label.setObjectName(u"song_id_label")
        self.song_id_label.setMaximumSize(QSize(195, 16777215))
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.song_id_label.sizePolicy().hasHeightForWidth())
        self.song_id_label.setSizePolicy(sizePolicy6)

        self.verticalLayout_3.addWidget(self.song_id_label)

        self.farc_song_id_spinbox = QDoubleSpinBox(self.to_farc_tab)
        self.farc_song_id_spinbox.setMaximumSize(QSize(195, 16777215))
        self.farc_song_id_spinbox.setObjectName(u"farc_song_id_spinbox")
        self.farc_song_id_spinbox.setDecimals(0)
        self.farc_song_id_spinbox.setMinimum(1.000000000000000)
        self.farc_song_id_spinbox.setMaximum(4294967295.000000000000000)
        self.farc_song_id_spinbox.setValue(1.000000000000000)

        self.verticalLayout_3.addWidget(self.farc_song_id_spinbox)


        self.farc_compression_label = QLabel(self.to_farc_tab)
        self.farc_compression_label.setMaximumSize(QSize(195, 16777215))
        self.farc_compression_label.setText("Compression:")

        self.verticalLayout_3.addWidget(self.farc_compression_label)

        self.farc_compression_dropdown = QEnumComboBox()
        self.farc_compression_dropdown.setMaximumSize(QSize(195, 16777215))
        self.farc_compression_dropdown.setEnumClass(Compression)

        self.verticalLayout_3.addWidget(self.farc_compression_dropdown)


        self.farc_export_button = QPushButton(self.to_farc_tab)
        self.farc_export_button.setMaximumSize(QSize(195, 16777215))
        self.farc_export_button.setObjectName(u"farc_export_button")

        self.verticalLayout_3.addWidget(self.farc_export_button)

        self.farc_create_thumbnail_button = QPushButton(self.to_farc_tab)
        self.farc_create_thumbnail_button.setMaximumSize(QSize(195, 16777215))
        self.farc_create_thumbnail_button.setObjectName(u"farc_create_thumbnail_button")

        self.verticalLayout_3.addWidget(self.farc_create_thumbnail_button)

        self.generate_spr_db_button = QPushButton(self.to_farc_tab)
        self.generate_spr_db_button.setObjectName(u"generate_spr_db_button")
        self.generate_spr_db_button.setMaximumSize(QSize(195, 16777215))
        self.generate_spr_db_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.verticalLayout_3.addWidget(self.generate_spr_db_button)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.export_controls.addTab(self.to_farc_tab, "")
        self.to_image_tab = QWidget()
        self.to_image_tab.setObjectName(u"to_image_tab")
        self.verticalLayout_4 = QVBoxLayout(self.to_image_tab)
        self.verticalLayout_4.setSpacing(4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(4, 4, 4, 4)
        self.open_preview_button = QPushButton(self.to_image_tab)
        self.open_preview_button.setSizePolicy(sizePolicy)
        self.open_preview_button.setMaximumSize(QSize(195, 16777215))
        self.open_preview_button.setObjectName(u"open_preview_button")

        self.verticalLayout_4.addWidget(self.open_preview_button)

        self.copy_to_clipboard_button = QPushButton(self.to_image_tab)
        self.copy_to_clipboard_button.setObjectName(u"copy_to_clipboard_button")
        sizePolicy.setHeightForWidth(self.copy_to_clipboard_button.sizePolicy().hasHeightForWidth())
        self.copy_to_clipboard_button.setSizePolicy(sizePolicy)
        self.copy_to_clipboard_button.setMaximumSize(QSize(195, 16777215))
        self.copy_to_clipboard_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.verticalLayout_4.addWidget(self.copy_to_clipboard_button)

        self.export_thumbnail_button = QPushButton(self.to_image_tab)
        self.export_thumbnail_button.setObjectName(u"export_thumbnail_button")
        sizePolicy.setHeightForWidth(self.export_thumbnail_button.sizePolicy().hasHeightForWidth())
        self.export_thumbnail_button.setSizePolicy(sizePolicy)
        self.export_thumbnail_button.setMaximumSize(QSize(195, 16777215))
        self.export_thumbnail_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.verticalLayout_4.addWidget(self.export_thumbnail_button)

        self.export_logo_button = QPushButton(self.to_image_tab)
        self.export_logo_button.setObjectName(u"export_logo_button")
        sizePolicy.setHeightForWidth(self.export_logo_button.sizePolicy().hasHeightForWidth())
        self.export_logo_button.setSizePolicy(sizePolicy)
        self.export_logo_button.setMaximumSize(QSize(195, 16777215))
        self.export_logo_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.verticalLayout_4.addWidget(self.export_logo_button)

        self.export_background_jacket_button = QPushButton(self.to_image_tab)
        self.export_background_jacket_button.setObjectName(u"export_background_jacket_button")
        sizePolicy.setHeightForWidth(self.export_background_jacket_button.sizePolicy().hasHeightForWidth())
        self.export_background_jacket_button.setSizePolicy(sizePolicy)
        self.export_background_jacket_button.setMaximumSize(QSize(195, 16777215))
        self.export_background_jacket_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.verticalLayout_4.addWidget(self.export_background_jacket_button)

        self.verticalSpacer_2 = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.export_controls.addTab(self.to_image_tab, "")

        self.image_tab_vertical_layout.addWidget(self.export_controls)


        self.load_buttons_box.addLayout(self.image_tab_vertical_layout)


        self.horizontalLayout_5.addLayout(self.load_buttons_box)

        MainWindow.setCentralWidget(self.grid)

        self.retranslateUi(MainWindow)

        self.current_sprite_combobox.setCurrentIndex(1)
        self.sprite_controls.setCurrentIndex(1)
        self.export_controls.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        self.has_logo_checkbox.setText(QCoreApplication.translate("MainWindow", u"Has logo?", None))
        self.new_classics_checkbox.setText(QCoreApplication.translate("MainWindow", u"New Classics?", None))
        self.current_sprite_combobox.setItemText(0, QCoreApplication.translate("MainWindow", u"Jacket", None))
        self.current_sprite_combobox.setItemText(1, QCoreApplication.translate("MainWindow", u"Background", None))
        self.current_sprite_combobox.setItemText(2, QCoreApplication.translate("MainWindow", u"Thumbnail", None))
        self.current_sprite_combobox.setItemText(3, QCoreApplication.translate("MainWindow", u"Logo", None))

        self.flip_horizontal_button.setText(QCoreApplication.translate("MainWindow", u"Flip Horizontally", None))
        self.flip_vertical_button.setText(QCoreApplication.translate("MainWindow", u"Flip Vertically", None))
        self.song_id_label.setText(QCoreApplication.translate("MainWindow", u"Song ID", None))
        self.farc_export_button.setText(QCoreApplication.translate("MainWindow", u"Export BG/JK/Logo Farc", None))
        self.farc_create_thumbnail_button.setText(QCoreApplication.translate("MainWindow", u"Create Thumbnail Farc", None))
        self.generate_spr_db_button.setText(QCoreApplication.translate("MainWindow", u"Generate Sprite Database", None))
        self.export_controls.setTabText(self.export_controls.indexOf(self.to_farc_tab), QCoreApplication.translate("MainWindow", u"To Farc", None))
        self.open_preview_button.setText(QCoreApplication.translate("MainWindow", u"Open preview externally", None))
        self.copy_to_clipboard_button.setText(QCoreApplication.translate("MainWindow", u"Copy preview to clipboard", None))
        self.export_thumbnail_button.setText(QCoreApplication.translate("MainWindow", u"Export Thumbnail", None))
        self.export_logo_button.setText(QCoreApplication.translate("MainWindow", u"Export Logo", None))
        self.export_background_jacket_button.setText(QCoreApplication.translate("MainWindow", u"Export Background/Jacket", None))
        self.export_controls.setTabText(self.export_controls.indexOf(self.to_image_tab), QCoreApplication.translate("MainWindow", u"To Image", None))
        pass
    # retranslateUi

