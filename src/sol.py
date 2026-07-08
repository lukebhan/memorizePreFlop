import os
import sys
from glob import glob

from PyQt5.QtCore import Qt
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from customButton import DrawScenarioButton, DrawRangeButton, DrawReportButton
from trainingReports import TrainingReports
from rangeBuilder import RangeBuilder
from handTrainer import HandTrainer
from chartTrainer import ChartTrainer
from reports import Report
import numpy as np

class simul(QMainWindow):
    def __init__(self):
        super().__init__()
        # Fonts

        self.setWindowTitle("Memorize PreFlop")
        # Zoom level applied on top of FONT_SCALE via Ctrl + mouse wheel.
        self.zoom = 1.0
        self.mainWidget = QWidget()
        # Scroll area so zoomed-in content can overflow with scrollbars instead
        # of forcing the window larger.
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.mainWidget)
        self.setCentralWidget(self.scrollArea)
        # Small minimum so the whole UI can be dragged down to fit small windows.
        self.setMinimumSize(400, 300)
        self.layout = QGridLayout(self.mainWidget)

        self.titleWidget = QLabel("Memorize PreFlop")
        self.titleWidget.setFont(self.font(30))
        self.layout.addWidget(self.titleWidget, 0, 0, Qt.AlignCenter)
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.tabWidget = QTabWidget()

        self.tabWidget.insertTab(4, self.trainingReports(), "Training Reports")
        self.tabWidget.insertTab(0, self.rangeBuilderFunc(), "Range Builder")
        self.tabWidget.insertTab(1, self.chartTrainerFunc(), "Chart Trainer")
        self.tabWidget.insertTab(2, self.handTrainerFunc(), "Hand Trainer")
        self.tabWidget.setFont(self.font(25))
        self.tabWidget.setCurrentIndex(0)   
        self.innerLayout = QGridLayout()
        self.innerLayout.setContentsMargins(10, 10, 10, 10)
        self.layout.addLayout(self.innerLayout, 1, 0)
        self.innerLayout.addWidget(self.tabWidget, 1, 0)

        # Catch Ctrl + wheel anywhere in the app to zoom the whole UI.
        QApplication.instance().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Wheel and (event.modifiers() & Qt.ControlModifier):
            delta = event.angleDelta().y()
            if delta != 0:
                self.setZoom(self.zoom * (1.1 if delta > 0 else 1/1.1))
            return True
        return super().eventFilter(obj, event)

    def setZoom(self, newZoom):
        newZoom = max(0.5, min(3.0, newZoom))
        if abs(newZoom - self.zoom) < 1e-6:
            return
        old = self.zoom
        widgets = self.findChildren(QWidget)
        # Pass 1: capture each widget's base (zoom 1.0) font size BEFORE touching
        # any font, so inherited fonts are not re-read after being enlarged.
        for wdg in widgets:
            if wdg.property("_baseFontPS") is None:
                ps = wdg.font().pointSizeF()
                if ps > 0:
                    wdg.setProperty("_baseFontPS", ps / old)
        # Pass 2: set each font absolutely from its base, so zoom never compounds.
        for wdg in widgets:
            base = wdg.property("_baseFontPS")
            if base is not None:
                f = wdg.font()
                f.setPointSizeF(max(4.0, base * newZoom))
                wdg.setFont(f)
        self.zoom = newZoom
        self.applyGridZoom()

    def applyGridZoom(self):
        # Grid cells stay fully collapsible at/below 1.0 (so the window can be
        # made small); above 1.0 they grow and the scroll area scrolls.
        cell = int(26 * self.zoom)
        for button in self.findChildren(DrawRangeButton) + self.findChildren(DrawReportButton):
            if self.zoom > 1.0:
                button.setMinimumSize(cell, cell)
            else:
                button.setMinimumSize(1, 1)

    def generateFirstReport(self):
        if not hasattr(self, 'reports'):
            comboMap, comboMapInverse = self.generateMap()
            self.reports = Report(comboMap, comboMapInverse, "True")

    def generateMap(self):
        cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
        inverseMap = {}
        combo = []
        for i in range(len(cards)):
            # Goes from 0 to 12
            # Then from 1 to 12
            for j in range(i+1):
                if i!=j:
                    combo.append(cards[j]+cards[i]+"o")
                    inverseMap[cards[j]+cards[i]+"o"] = [j, i]
            for j in range(i, 13):
                if i!=j:
                    combo.append(cards[i]+cards[j]+"s") 
                    inverseMap[cards[i]+cards[j]+"s"] = [j, i]
                else:
                    combo.append(cards[i]+cards[j]) 
                    inverseMap[cards[i]+cards[j]] = [j, i]
        return np.array(combo).reshape((13, 13)).transpose(), inverseMap

    # Font sizes throughout the app are requested at their original scale; we
    # scale them down here so the fixed-size text does not force a large minimum
    # window size. Change FONT_SCALE alone to retune the whole UI.
    FONT_SCALE = 0.5

    def font(self, size):
        return QFont("courier 10 pitch", max(6, int(size * self.FONT_SCALE * self.zoom)))

    def rangeBuilderFunc(self):
        comboMap, comboMapInverse = self.generateMap()
        self.rangeBuilder = RangeBuilder(self, comboMap, comboMapInverse, self.font)
        return self.rangeBuilder.getWindow()

    def handTrainerFunc(self):
        return self.handTrainer.getWindow()

    def chartTrainerFunc(self):
        return self.chartTrainer.getWindow()

    def trainingReports(self):
        comboMap, comboMapInverse = self.generateMap()
        self.generateFirstReport()
        self.trainingReports = TrainingReports(self, comboMap, comboMapInverse, self.font, self.reports)
        self.chartTrainer = ChartTrainer(self, comboMap, comboMapInverse, self.font, self.reports)
        self.handTrainer = HandTrainer(self, comboMap, self.font, self.reports)
        return self.trainingReports.getWindow()


if __name__ == "__main__":
    # When running as a bundled (PyInstaller) app, the card images, ranges and
    # reports are shipped next to the executable. Switch to that directory so
    # the app's relative paths resolve no matter where it is launched from.
    if getattr(sys, "frozen", False):
        os.chdir(os.path.dirname(sys.executable))
    app = QApplication(sys.argv)
    window = simul()
    window.show()
    sys.exit(app.exec())
