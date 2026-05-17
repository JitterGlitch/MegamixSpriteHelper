from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QLabel,
                               QLayout, QLineEdit, QPushButton, QScrollArea,
                               QSizePolicy, QVBoxLayout, QWidget, QDoubleSpinBox)
from widgets import PlaceholderDoubleSpinBox

class Ui_ThumbnailIDField(object):
        def setupUi(self, Form, variant):
                if not Form.objectName():
                        Form.setObjectName(u"Form")
                Form.resize(208, 45)
                self.formLayout = QFormLayout(Form)
                self.formLayout.setObjectName(u"formLayout")
                self.formLayout.setContentsMargins(0, 0, 0, 0)

                self.song_id_spinbox = PlaceholderDoubleSpinBox(Form)
                self.song_id_spinbox.setObjectName(u"song_id_spinbox")
                self.song_id_spinbox.setMinimumSize(QSize(154, 0))
                self.song_id_spinbox.setDecimals(0)
                self.song_id_spinbox.setMaximum(4294967295.000000000000000)
                sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.song_id_spinbox.sizePolicy().hasHeightForWidth())
                self.song_id_spinbox.setSizePolicy(sizePolicy)
                self.song_id_spinbox.setMinimumSize(QSize(154, 27))
                self.song_id_spinbox.setMaximumSize(QSize(154, 27))
                self.song_id_spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

                self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.song_id_spinbox)

                match variant:
                        case False:
                                self.id_line_button = QPushButton(Form)
                                self.id_line_button.setObjectName(u"id_line_button")
                                sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
                                sizePolicy1.setHorizontalStretch(0)
                                sizePolicy1.setVerticalStretch(0)
                                sizePolicy1.setHeightForWidth(self.id_line_button.sizePolicy().hasHeightForWidth())
                                self.id_line_button.setSizePolicy(sizePolicy1)
                                self.id_line_button.setMinimumSize(QSize(30, 27))
                                self.id_line_button.setMaximumSize(QSize(30, 27))
                                self.id_line_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                                self.id_line_button.setIcon(QPixmap(":icon/Images/Minus.png"))
                                palette = QPalette()
                                brush = QBrush(QColor(235,51,101, 255))
                                brush.setStyle(Qt.BrushStyle.SolidPattern)
                                palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush)
                                self.id_line_button.setPalette(palette)

                                self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.id_line_button)

                                QMetaObject.connectSlotsByName(Form)
                                self.retranslateUi(Form,False)
                        case True:
                                self.id_line_button = QPushButton(Form)
                                self.id_line_button.setObjectName(u"id_line_button")
                                sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
                                sizePolicy1.setHorizontalStretch(0)
                                sizePolicy1.setVerticalStretch(0)
                                sizePolicy1.setHeightForWidth(self.id_line_button.sizePolicy().hasHeightForWidth())
                                self.id_line_button.setMinimumSize(QSize(30, 27))
                                self.id_line_button.setMaximumSize(QSize(30, 27))
                                self.id_line_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                                self.id_line_button.setIcon(QPixmap(":icon/Images/Plus.png"))
                                palette = QPalette()
                                brush = QBrush(QColor(51, 235, 101, 255))
                                brush.setStyle(Qt.BrushStyle.SolidPattern)
                                palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush)
                                self.id_line_button.setPalette(palette)

                                self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.id_line_button)

                                QMetaObject.connectSlotsByName(Form)
                                self.retranslateUi(Form, True)


        # setupUi

        def retranslateUi(self, Form,variant):
                Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
                match variant:
                    case False:#Remove
                        self.song_id_spinbox.setSpecialValueText(QCoreApplication.translate("Form", u"Set additional ID", None))

                    case True:#Add
                        self.song_id_spinbox.setSpecialValueText(QCoreApplication.translate("Form", u"Set Song ID", None))
                # retranslateUi

