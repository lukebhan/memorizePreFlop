import os
import sys
from glob import glob

from PyQt5.QtCore import Qt
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from customButton import DrawScenarioButton
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
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.layout = QGridLayout(self.mainWidget)

        self.titleWidget = QLabel("Memorize PreFlop")
        self.titleWidget.setFont(self.font(30))
        self.layout.addWidget(self.titleWidget, 0, 0, Qt.AlignCenter)
        self.layout.setContentsMargins(30, 30, 30, 30)

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

    def font(self, size):
        return QFont("courier 10 pitch", size)

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
    app = QApplication(sys.argv)
    window = simul()
    window.show()
    sys.exit(app.exec())
