import re
from enum import Enum

from PySide6.QtCore import (Qt, QTimer, QEvent, Signal)
from PySide6.QtGui import (QBrush, QColor, QPalette, QMouseEvent, QPixmap)
from PySide6.QtWidgets import (QDoubleSpinBox, QHBoxLayout,
                               QLabel, QPushButton,
                               QSpinBox, QWidget, QMenu, QScrollArea, QVBoxLayout, QComboBox)
from superqt import QSearchableComboBox, QEnumComboBox, QIconifyIcon


class Stylesheet(Enum):
    SCROLL_AREA_CONFLICT = ".OuterFrame {border: 1px solid rgb(235,51,101);border-radius: 2px;}"
    SCROLL_AREA_UNFILLED = ".OuterFrame {border: 1px solid rgb(123,104,238);border-radius: 2px;}"
    ID_FIELD_CONFLICT = ".PlaceholderDoubleSpinBox {color: rgb(235,51,101);}"
    ID_FIELD_PLACEHOLDER = ".PlaceholderDoubleSpinBox {color: rgb(155,155,155);}"
    SPRITE_VALUE_LABEL =":hover {background-color: rgba(155,155,155,50);}"
    LABEL_PLACEHOLDER = ".QLabel {color: rgb(155,155,155);}"
    LINE_PLACEHOLDER = ".QLineEdit {color: rgb(155,155,155);}"

#TODO Replace this with setObjectName and then searching for that -- No need to use SubClass
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
        action = self.actionAt(event.pos())
        if action and action.isCheckable():
            action.trigger()
            event.accept()
        else:
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
        self.delete_button.setIcon(QIconifyIcon("tabler:minus", color="red").pixmap(27, 27))
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

