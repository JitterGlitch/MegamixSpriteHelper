import re
from enum import Enum

from PySide6.QtCore import (QSize, Qt, Signal, QTimer)
from PySide6.QtGui import (QBrush, QColor, QFont, QPalette, QMouseEvent, QPixmap, QAction)
from PySide6.QtWidgets import (QDoubleSpinBox, QHBoxLayout,
                               QLabel, QPushButton,
                               QSpinBox,
                               QVBoxLayout, QWidget, QSlider, QMenu)
from superqt import QDoubleSlider, QSearchableComboBox

class Stylesheet(Enum):
    SCROLL_AREA_CONFLICT = ".QScrollArea {border: 1px solid rgb(235,51,101);border-radius: 2px;}"
    SCROLL_AREA_UNFILLED = ".QScrollArea {border: 1px solid rgb(123,104,238);border-radius: 2px;}"
    ID_FIELD_CONFLICT = ".PlaceholderDoubleSpinBox {color: rgb(235,51,101);}"
    ID_FIELD_PLACEHOLDER = ".PlaceholderDoubleSpinBox {color: rgb(155,155,155);}"
    SPRITE_VALUE_LABEL =":hover {background-color: rgba(155,155,155,50);}"
    LABEL_PLACEHOLDER = ".QLabel {color: rgb(155,155,155);}"

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
        self.label = QLabel()
        self.label.mousePressEvent = self.on_label_clicked
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setText("Enter your mod name here")
        self.label.setStyleSheet(Stylesheet.LABEL_PLACEHOLDER.value)

        self.combo_box = QSearchableComboBox()
        self.combo_box.setEditable(True)
        self.combo_box.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.combo_box.setPlaceholderText("Enter your mod name here")

        palette = QPalette()
        brush = QBrush(QColor(235, 51, 101, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush)

        self.delete_button = QPushButton()
        self.delete_button.setPalette(palette)
        self.delete_button.setIcon(QPixmap(":icon/Images/Minus.png"))
        self.delete_button.setFixedSize(30,27)

        self.combo_box.installEventFilter(self)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo_box)
        self.layout.addWidget(self.delete_button)

        self.label.setVisible(True)
        self.combo_box.setVisible(False)

    def on_label_clicked(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_editing()

    def start_editing(self):
        self.label.setVisible(False)
        self.combo_box.setVisible(True)
        self.combo_box.setFocus()

    def label_set_placeholder_text(self):
        self.label.setText("Enter your mod name here")
        self.label.setStyleSheet(Stylesheet.LABEL_PLACEHOLDER.value)

    def finish_editing(self):
        if self.get_filtered_text():
            self.label.setText(self.get_filtered_text())
            self.label.setStyleSheet("")
        else:
            self.label_set_placeholder_text()


        self.combo_box.setVisible(False)
        self.label.setVisible(True)

    def get_filtered_text(self):
        mod_string = self.combo_box.currentText()
        mod_string = re.sub(r'[^A-Za-z0-9_ ]+', '', mod_string)

        return "_".join(mod_string.split())

    def eventFilter(self, watched, event, /):
        if watched == self.combo_box and event.type() == event.Type.FocusOut:
            if self.hasFocus():
                event.ignore()
            else:
                QTimer.singleShot(100, self.finish_editing)
        return super().eventFilter(watched, event)