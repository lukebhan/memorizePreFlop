from PyQt5.QtCore import Qt
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class DrawRangeButton(QPushButton):
    def __init__(self, mainColor, text):
        super().__init__()
        self.mainColor = mainColor
        self.raiseColor = None
        self.callColor = None
        self.curHeight = 0
        self.raiseScale = 0
        self.callScale = 0
        self.text = text
        self.incorrect = False

    def paintEvent(self, event):
        r = event.rect()
        p = QPainter(self)
        p.fillRect(0, 0, int(r.width()), int(r.height()), Qt.black)
        p.fillRect(2, 2, int(r.width())-2, int(r.height())-2, QColor(self.mainColor))

                # we going to draw on top for filling
        if self.raiseScale != 0 and self.callScale != 0:
            # Draw both
            p.fillRect(2, 2, int((int(r.width())-2)*self.raiseScale), int(r.height())-2, QColor(self.raiseColor))
            p.fillRect(2+int(int(r.width()-2)*self.raiseScale), 2, int((int(r.width())-2)*self.callScale), int(r.height())-2, QColor(self.callColor))
        elif self.raiseScale != 0:
            # Draw raise scale  
            p.fillRect(2, 2, int((int(r.width())-2)*self.raiseScale), int(r.height())-2, QColor(self.raiseColor))
        elif self.callScale != 0:
            # Draw call scale
            p.fillRect(2, 2, int((int(r.width())-2)*self.callScale), int(r.height())-2, QColor(self.callColor))
        p.drawText(r, Qt.AlignCenter, self.text)
        if self.incorrect:
            p.fillRect(int(r.width()*0.75), int(r.height()*0.25), int(r.width()*0.18), int(r.height()*0.18), QColor("red"))

    def changeColorAndScale(self, color, scale, raiseOrCall):
        # Update raise
        if raiseOrCall == 1:
            if self.raiseScale == scale:
                self.raiseScale = 0
            else:
                if scale + self.callScale > 1:
                    QMessageBox.about(self, "Warning", "Call + Raise Percentage > 1. Percentage not updated")
                else:
                    self.raiseScale = scale
            self.raiseColor = color
        else:
            if self.callScale == scale:
                self.callScale = 0
            else:
                if scale + self.raiseScale > 1:
                    QMessageBox.about(self, "Warning", "Call + Raise Percentage > 1. Percentage not updated")
                else:
                    self.callScale = scale
            self.callColor = color
        self.update()

    def loadColorAndScale(self, color, scale, raiseOrCall):
        if raiseOrCall == 1:
            self.raiseScale = scale
            self.raiseColor = color
        else:
            self.callScale = scale
            self.callColor = color
        self.update()

    def changeColor(self, color, raiseOrCall):
        if raiseOrCall == 1:
            self.raiseColor = color
        else:
            self.callColor = color
        self.update()

    def clear(self):
        self.raiseScale = 0
        self.callScale = 0
        self.update()

    def getCallScale(self):
        return self.callScale

    def getRaiseScale(self):
        return self.raiseScale

    def markIncorrect(self):
        self.incorrect=True
        self.update()

    def markCorrect(self):
        self.incorrect=False

class DrawScenarioButton(QPushButton):
    def __init__(self, text):
        super().__init__()
        self.selected = False
        self.textVal = text

    def paintEvent(self, event):
        r = event.rect()
        p = QPainter(self)
        p.fillRect(0, 0, int(r.width()), int(r.height()), QColor("#FAF9F6"))
        if self.selected:
            p.fillRect(0, 0, int(r.width()), int(r.height()), QColor("000000"))
            p.fillRect(2, 2, int(r.width())-4, int(r.height())-4, QColor("#FAF9F6"))
        p.drawText(r, Qt.AlignCenter, self.textVal)

    def updateSelected(self):
        if self.selected:
            self.selected = False
        else:
            self.selected = True
        self.update()


