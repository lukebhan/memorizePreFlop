from PyQt5.QtCore import Qt
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class DragWidget(QWidget):
    drag = QtCore.pyqtSignal(QtCore.QPoint)
    def __init__(self):
        super().__init__()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.drag.emit(event.pos())
        super().mouseMoveEvent(event)
