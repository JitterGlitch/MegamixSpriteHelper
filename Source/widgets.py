import re
from enum import Enum

from PySide6.QtCore import (Qt, QTimer, QEvent, Signal)
from PySide6.QtGui import (QBrush, QColor, QPalette, QMouseEvent, QPixmap)
from PySide6.QtWidgets import (QDoubleSpinBox, QHBoxLayout,
                               QLabel, QPushButton,
                               QSpinBox, QWidget, QMenu, QScrollArea, QVBoxLayout, QComboBox)
from superqt import QSearchableComboBox, QEnumComboBox



class Stylesheet(Enum):
    SCROLL_AREA_CONFLICT = ".OuterFrame {border: 1px solid rgb(235,51,101);border-radius: 2px;}"
    SCROLL_AREA_UNFILLED = ".OuterFrame {border: 1px solid rgb(123,104,238);border-radius: 2px;}"
    ID_FIELD_CONFLICT = ".PlaceholderDoubleSpinBox {color: rgb(235,51,101);}"
    ID_FIELD_PLACEHOLDER = ".PlaceholderDoubleSpinBox {color: rgb(155,155,155);}"
    SPRITE_VALUE_LABEL =":hover {background-color: rgba(155,155,155,50);}"
    LABEL_PLACEHOLDER = ".QLabel {color: rgb(155,155,155);}"
    LINE_PLACEHOLDER = ".QLineEdit {color: rgb(155,155,155);}"

class OuterFrame(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class PlaceholderDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workaround = True
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event, /):
        if self.hasFocus():
            QSpinBox.wheelEvent(self, event)
        else:
            event.ignore()

    def focusInEvent(self, event):
        #TODO do it properly // Shitty workaround for setupUi being executed bit later than init
        if self.workaround:
            self.setSpecialValueText(self.specialValueText())
            self.setPlaceholderText(self.specialValueText())
            self.workaround = False

        if self.value() == self.minimum():
            self.setSpecialValueText("")
        super().focusInEvent(event)
        QTimer.singleShot(10, self.selectAll)


    def focusOutEvent(self, event):
        if self.value() == self.minimum():
            self.setSpecialValueText(self.placeholderText())
        super().focusOutEvent(event)

    def setPlaceholderText(self, text):
        self._placeholder_text = text
        self.setSpecialValueText(text)

    def placeholderText(self):
        return getattr(self, '_placeholder_text', "")
class QSmarterMenu(QMenu):
    def mouseReleaseEvent(self, event):
        # Get the action at the click position
        action = self.actionAt(event.pos())
        # If the action exists and is checkable, handle it manually
        if action and action.isCheckable():
            # Trigger the action (toggles its checked state)
            action.trigger()
            # Accept the event to prevent further processing
            event.accept()
            # Do NOT call super(), so the menu stays open
        else:
            # For non-checkable actions or clicks on empty area, let the menu close normally
            super().mouseReleaseEvent(event)

class SongpackNameInput(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.combo_box = QSearchableComboBox()
        self.combo_box.setEditable(True)
        self.combo_box.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.combo_box.lineEdit().editingFinished.connect(self.clean_up_text)
        self.combo_box.lineEdit().setPlaceholderText("Enter your mod name here")

        palette = QPalette()
        brush = QBrush(QColor(235, 51, 101, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush)

        self.delete_button = QPushButton()
        self.delete_button.setPalette(palette)
        self.delete_button.setIcon(QPixmap(":icon/Images/Minus.png"))
        self.delete_button.setFixedSize(30,27)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        self.layout.addWidget(self.combo_box)
        self.layout.addWidget(self.delete_button)

        self.combo_box.setVisible(True)

    def get_filtered_text(self):
        mod_string = self.combo_box.currentText()
        mod_string = re.sub(r'[^A-Za-z0-9_ ]+', '', mod_string)

        return "_".join(mod_string.split())
    def clean_up_text(self):
        self.combo_box.setCurrentText(self.get_filtered_text())

class SpriteGroupPreview(QWidget):
    SpriteGroupChanged = Signal()
    def __init__(self,sprite_group_name:str,SC_obj,sprite_group):
        super().__init__()
        self.SC = SC_obj
        self.max_H = 100
        self._first_run = True
        self._prev_enum = None
        self.sprite_group_enum = sprite_group
        self.create_ui(sprite_group_name)
        self.group_combobox.currentEnumChanged.connect(self.change_enum)

    def create_ui(self,sprite_group_name):
        self.setMaximumHeight(150)
        self.sprite_group_Hlayout = QHBoxLayout()

        self.group_label = QLabel()
        self.group_label.setText(sprite_group_name)

        self.group_combobox = QEnumComboBox()
        self.group_combobox.setEnumClass(self.sprite_group_enum)
        self._prev_enum = self.group_combobox.currentEnum()

        self.sprite_group_Hlayout.addWidget(self.group_label)
        self.sprite_group_Hlayout.addWidget(self.group_combobox)


        self.preview_Hlayout = QHBoxLayout()

        self.background_label = QLabel()
        self.background_label.setPixmap(self.SC.enum_to_obj(self.group_combobox.currentEnum()).background.pixmap().scaledToHeight(self.max_H))

        self.jacket_label = QLabel()
        self.jacket_label.setPixmap(self.SC.enum_to_obj(self.group_combobox.currentEnum()).jacket.pixmap().scaledToHeight(self.max_H))

        self.logo_label = QLabel()
        self.logo_label.setPixmap(self.SC.enum_to_obj(self.group_combobox.currentEnum()).logo.pixmap().scaledToHeight(self.max_H))

        self.preview_Hlayout.addWidget(self.background_label)
        self.preview_Hlayout.addWidget(self.jacket_label)
        self.preview_Hlayout.addWidget(self.logo_label)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self.sprite_group_Hlayout)
        self.main_layout.addLayout(self.preview_Hlayout)

        self.change_enum()

    def change_enum(self):
        if not self._first_run:
            self.SC.enum_to_obj(self._prev_enum).background.SpriteUpdated.disconnect(self.change_preview)
            self.SC.enum_to_obj(self._prev_enum).jacket.SpriteUpdated.disconnect(self.change_preview)
            self.SC.enum_to_obj(self._prev_enum).logo.SpriteUpdated.disconnect(self.change_preview)
            self._first_run = False


        self.SC.enum_to_obj(self.group_combobox.currentEnum()).background.SpriteUpdated.connect(self.change_preview)
        self.SC.enum_to_obj(self.group_combobox.currentEnum()).jacket.SpriteUpdated.connect(self.change_preview)
        self.SC.enum_to_obj(self.group_combobox.currentEnum()).logo.SpriteUpdated.connect(self.change_preview)

        self._prev_enum = self.group_combobox.currentEnum()
        self.change_preview()
        self.SpriteGroupChanged.emit()

    def get_selected_sprite_group(self):
        return self.group_combobox.currentEnum()


    def change_preview(self):
        self.background_label.setPixmap(self.SC.enum_to_obj(self.group_combobox.currentEnum()).background.pixmap().scaledToHeight(self.max_H))
        self.jacket_label.setPixmap(self.SC.enum_to_obj(self.group_combobox.currentEnum()).jacket.pixmap().scaledToHeight(self.max_H))
        self.logo_label.setPixmap(self.SC.enum_to_obj(self.group_combobox.currentEnum()).logo.pixmap().scaledToHeight(self.max_H))
