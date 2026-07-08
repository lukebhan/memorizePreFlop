from PyQt5.QtCore import Qt
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


def scaledFont(widget, rect, ratio=0.42, minSize=4):
    # A font sized to the current cell so grid text scales with the window
    f = widget.font()
    f.setPixelSize(max(minSize, int(min(rect.width(), rect.height()) * ratio)))
    return f


class DrawRangeButton(QPushButton):
    drag = QtCore.pyqtSignal(QtCore.QPoint)
    def __init__(self, mainColor, text):
        super().__init__()
        self.mainColor = mainColor
        self.raiseColor = None
        self.callColor = None
        self.allinColor = None
        self.curHeight = 0
        self.raiseScale = 0
        self.callScale = 0
        self.allinScale = 0
        self.text = text
        self.incorrect = False
        # Let the button shrink/grow with the window instead of forcing a large
        # minimum size from its font; the text is scaled to fit in paintEvent.
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(1, 1)

    def paintEvent(self, event):
        r = event.rect()
        p = QPainter(self)
        p.fillRect(0, 0, int(r.width()), int(r.height()), Qt.black)
        p.fillRect(2, 2, int(r.width())-2, int(r.height())-2, QColor(self.mainColor))

        # Draw each category segment side by side, offset by the previous ones
        width = int(r.width())-2
        height = int(r.height())-2
        offset = 2
        for scale, color in ((self.raiseScale, self.raiseColor),
                             (self.callScale, self.callColor),
                             (self.allinScale, self.allinColor)):
            if scale != 0:
                p.fillRect(offset, 2, int(width*scale), height, QColor(color))
                offset += int(width*scale)
        p.setFont(scaledFont(self, r))
        p.drawText(r, Qt.AlignCenter, self.text)
        if self.incorrect:
            p.fillRect(int(r.width()*0.75), int(r.height()*0.25), int(r.width()*0.18), int(r.height()*0.18), QColor("red"))

    def changeColorAndScale(self, color, scale, raiseOrCall):
        # raiseOrCall: 1 = raise, 0 = call, 2 = all-in
        if raiseOrCall == 1:
            cur, others = self.raiseScale, self.callScale + self.allinScale
        elif raiseOrCall == 2:
            cur, others = self.allinScale, self.raiseScale + self.callScale
        else:
            cur, others = self.callScale, self.raiseScale + self.allinScale

        if cur == scale:
            newScale = 0
        elif scale + others > 1:
            QMessageBox.about(self, "Warning", "Raise + Call + All-In Percentage > 1. Percentage not updated")
            newScale = cur
        else:
            newScale = scale

        if raiseOrCall == 1:
            self.raiseScale = newScale
            self.raiseColor = color
        elif raiseOrCall == 2:
            self.allinScale = newScale
            self.allinColor = color
        else:
            self.callScale = newScale
            self.callColor = color
        self.update()

    def loadColorAndScale(self, color, scale, raiseOrCall):
        if raiseOrCall == 1:
            self.raiseScale = scale
            self.raiseColor = color
        elif raiseOrCall == 2:
            self.allinScale = scale
            self.allinColor = color
        else:
            self.callScale = scale
            self.callColor = color
        self.update()

    def changeColor(self, color, raiseOrCall):
        if raiseOrCall == 1:
            self.raiseColor = color
        elif raiseOrCall == 2:
            self.allinColor = color
        else:
            self.callColor = color
        self.update()

    def clear(self):
        self.raiseScale = 0
        self.callScale = 0
        self.allinScale = 0
        self.update()

    def getCallScale(self):
        return self.callScale

    def getRaiseScale(self):
        return self.raiseScale

    def getAllinScale(self):
        return self.allinScale

    def markIncorrect(self):
        self.incorrect=True
        self.update()

    def markCorrect(self):
        self.incorrect=False
        self.clear()

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

class DrawReportButton(QPushButton):
    def __init__(self, mainColor, text):
        super().__init__()
        self.text = text
        self.mainColor = mainColor
        self.curColor = mainColor
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(1, 1)

    def paintEvent(self, event):
        r = event.rect()
        p = QPainter(self)
        p.fillRect(0, 0, int(r.width()), int(r.height()), Qt.black)
        p.fillRect(2, 2, int(r.width())-2, int(r.height())-2, QColor(self.curColor))
        p.setFont(scaledFont(self, r))
        p.drawText(r, Qt.AlignCenter, self.text)

    def updateButton(self, total, correct):
        if total == 0:
            self.curColor = self.mainColor
        else:
            percentage = float(correct)/float(total)
            if percentage < 0.1:
                self.curColor = "#FF0000"
            elif percentage >= 0.1 and percentage < 0.2:
                self.curColor = "#e73b00"
            elif percentage >= 0.2 and percentage < 0.3:
                self.curColor = "#ce5100"
            elif percentage >= 0.3 and percentage < 0.4:
                self.curColor = "#b45f00"
            elif percentage >= 0.4 and percentage < 0.5:
                self.curColor = "#9a6900"
            elif percentage >= 0.5 and percentage < 0.6:
                self.curColor = "#806f00"
            elif percentage >= 0.6 and percentage < 0.7:
                self.curColor = "#677200"
            elif percentage >= 0.7 and percentage < 0.8:
                self.curColor = "#4d7300"
            elif percentage >= 0.8 and percentage < 0.9:
                self.curColor = "#317300"
            else:
                self.curColor = "#027202"
        self.update()
            
    def reset(self):
        self.curColor = self.mainColor
        self.update()



