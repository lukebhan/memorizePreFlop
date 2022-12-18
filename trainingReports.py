from PyQt5.QtCore import Qt
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from customButton import DrawReportButton
from functools import partial
from colorPicker import ColorButton
from parser import *
import os

class TrainingReports():
    def __init__(self, mainWindow, comboMap, comboMapInverse, font, report):
        global reportActive
        self.generalTab = QWidget()
        self.mainLayout = QHBoxLayout()

        self.comboMap = comboMap
        self.comboMapInverse = comboMapInverse
        self.buttonPushMap = []
        # function for font building
        self.font = font
        self.main = mainWindow
        self.report = report

    def buildMain(self):
        self.leftLayout = self.buildLeftLayout()
        self.rightLayout = self.buildRightLayout()
        self.mainLayout.addLayout(self.leftLayout, 4)
        self.mainLayout.addLayout(self.rightLayout, 1)
        self.generalTab.setLayout(self.mainLayout)

    def getWindow(self):
        self.buildMain()
        return self.generalTab

    def buildLeftLayout(self):
        leftLayout = QVBoxLayout()
        leftLayout.setContentsMargins(70, 20, 70, 10)
        self.rangeLabel = QLabel("Total Report", alignment=Qt.AlignCenter)
        leftLayout.addWidget(self.rangeLabel, 1)
        leftLayout.addWidget(self.buildButtonLayout(), 6)
        leftLayout.addLayout(self.buildStatisticsTable(), 3)
        return leftLayout

    def buildRightLayout(self):
        rightLayout = QVBoxLayout()
        rightLayout.setContentsMargins(0,200, 0, 70)
        rightLayout.addLayout(self.buildRefreshButton())
        rightLayout.addLayout(self.buildNameEdit())
        rightLayout.addLayout(self.buildNewButtons())
        rightLayout.addLayout(self.buildPauseButtons())
        rightLayout.addLayout(self.createRangeBrowser())
        rightLayout.addLayout(self.buildLoadSaveButtons())
        rightLayout.addStretch()
        return rightLayout

    def buildRefreshButton(self):
        button = QPushButton("Refresh")
        button.clicked.connect(self.refresh)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(button)
        buttonLayout.setContentsMargins(0, 20, 20, 20)
        return buttonLayout

    def buildNewButtons(self):
        newPauseLayouts = QHBoxLayout()
        button=QPushButton("New Report")
        button.clicked.connect(self.newReport)
        newPauseLayouts.addWidget(button)
        newPauseLayouts.setContentsMargins(0, 0, 20, 20)
        return newPauseLayouts

    def buildNameEdit(self):
        newPauseLayouts = QHBoxLayout()
        nameLayout = QHBoxLayout()
        label = QLabel("Report Name")
        label.setFont(self.font(12))
        nameLayout.addWidget(label)
        nameLayout.setContentsMargins(0, 0, 5, 0)
        self.reportName= QLineEdit()
        self.reportName.setFont(self.font(12))
        self.reportName.setText("report1")
        newPauseLayouts.addLayout(nameLayout)
        newPauseLayouts.addWidget(self.reportName)
        newPauseLayouts.setContentsMargins(0, 20, 20, 10)
        return newPauseLayouts

    def buildPauseButtons(self):
        newPauseLayouts = QHBoxLayout()
        button2 = QPushButton("Pause/Continue")
        button2.clicked.connect(self.pauseReport)
        newPauseLayouts.addWidget(button2)
        newPauseLayouts.setContentsMargins(0, 20, 20, 20)
        return newPauseLayouts

    def buildLoadSaveButtons(self):
        loadSaveLayouts = QHBoxLayout()
        button=QPushButton("Load")
        button.clicked.connect(self.loadReport)
        button2 = QPushButton("Save")
        button2.clicked.connect(self.saveReport)
        loadSaveLayouts.addWidget(button)
        loadSaveLayouts.addWidget(button2)
        loadSaveLayouts.setContentsMargins(0, 20, 20, 20)
        return loadSaveLayouts

    def loadReport(self):
        res = self.report.loadReport(self.reportLineEdit.text())
        if not res:
            QMessageBox.about(self.main, "Error", "Unable to Load Report. Resetting to new report.")
            self.newReport()
        else:
            QMessageBox.about(self.main, "Success", "Report loaded successfully.")
            self.refresh()

    def saveReport(self):
        res = self.report.saveReport(self.reportLineEdit.text())
        if not res:
            QMessageBox.about(self.main, "Error", "Unable to Save Report")
        else:
            QMessageBox.about(self.main, "Success", "Report saved successfully.")

    def newReport(self):
        self.report.clearReport()
        self.report.generateReport(self.reportName.text())
        self.refresh()

    def pauseReport(self):
        if self.report.isActive():
            self.report.setInactive()
        else:
            self.report.setActive()

    def refresh(self):
        layout = self.leftLayout.takeAt(2)
        self.leftLayout.removeItem(layout)
        self.clearLayout(layout)
        self.leftLayout.addLayout(self.buildStatisticsTable(), 3)
        self.resetDraw()

    def buildButtonLayout(self):
        buttonMainLayout = QHBoxLayout()
        buttonMainLayout.setSpacing(0)
        buttonMainLayout.setContentsMargins(3, 3, 3, 3)

        self.buttonWidget = QWidget()
        self.buttonWidget.setLayout(buttonMainLayout)

        # Build out button matrix 
        self.firstButton = None
        for i in range(13):
            buttonSubLayout = QVBoxLayout()
            buttonArr = []
            for j in range(13):
                button = DrawReportButton("#36454F", self.comboMap[i][j])
                button.setFont(self.font(22))
                buttonSubLayout.addWidget(button)
                buttonArr.append(button)
            buttonMainLayout.addLayout(buttonSubLayout)
            self.buttonPushMap.append(buttonArr)
        return self.buttonWidget

    def createRangeBrowser(self):
        reportEditLayout = QHBoxLayout()
        reportEditLayout.setContentsMargins(0, 20, 20, 0)

        self.reportLineEdit = QLineEdit()
        self.reportLineEdit.setFont(self.font(12))
        self.reportLineEdit.setText("reports/")

        browseButton = QPushButton("Browse")
        browseButton.setFont(self.font(14))
        browseButton.clicked.connect(self.reportBrowserButtonCallback)
        reportEditLayout.addWidget(browseButton)
        reportEditLayout.addWidget(self.reportLineEdit)
        return reportEditLayout

    def reportBrowserButtonCallback(self):
        fileName, _ = QFileDialog().getOpenFileName(directory=os.getcwd()+"/reports/")
        fileName = fileName[len(os.getcwd())+1:] 
        self.reportLineEdit.setText(fileName)
        self.loadReport()

    def buildStatisticsTable(self):
        self.table = QTableWidget(0, 12)
        self.tableLayout = QHBoxLayout()
        self.tableLayout.setContentsMargins(0, 20, 0, 20)
        self.tableLayout.addWidget(self.table)
        self.table.setHorizontalHeaderItem(0, QTableWidgetItem("          Spot         "))
        self.table.setHorizontalHeaderItem(1, QTableWidgetItem("Number of\n   Hands   "))
        self.table.setHorizontalHeaderItem(2, QTableWidgetItem("Number of\n Hands Correct "))
        self.table.setHorizontalHeaderItem(3, QTableWidgetItem("Percent\n Correct "))
        self.table.setHorizontalHeaderItem(4, QTableWidgetItem("Number\n Raise Hands "))
        self.table.setHorizontalHeaderItem(5, QTableWidgetItem("Number\n Raise Correct "))
        self.table.setHorizontalHeaderItem(6, QTableWidgetItem("Percent\n Raise Correct "))
        self.table.setHorizontalHeaderItem(7, QTableWidgetItem("Number\n Call Hands "))
        self.table.setHorizontalHeaderItem(8, QTableWidgetItem("Number\n Call Correct "))
        self.table.setHorizontalHeaderItem(9, QTableWidgetItem("Percent\n Call Correct "))
        self.table.setHorizontalHeaderItem(10, QTableWidgetItem("Number\n Fold Hands "))
        self.table.setHorizontalHeaderItem(11, QTableWidgetItem("Number\n Fold Correct "))
        self.table.setHorizontalHeaderItem(12, QTableWidgetItem("Percent\n Fold Correct "))
        self.table.horizontalHeader().setFont(self.font(12))
        self.table.setFont(self.font(12))
        self.table.resizeColumnsToContents()
        self.table.verticalHeader().hide();
        self.table.doubleClicked.connect(self.drawSpot)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers);
        self.addReports()
        return self.tableLayout

    def addReports(self):
        self.keyArr = []
        if not self.report.isEmpty():
            self.curReport = self.report.getReport()
            for idx, key in enumerate(self.curReport["data"].keys()):
                self.keyArr.append(key)
                self.table.insertRow(self.table.rowCount());
                self.table.setItem(idx, 0, self.makeTableItem(key))
                self.table.setItem(idx, 1, self.makeTableItem(self.curReport["data"][key]["statistics"]["numberOfHands"]))
                self.table.setItem(idx, 2, self.makeTableItem(self.curReport["data"][key]["statistics"]["numberOfHandsCorrect"]))
                self.table.setItem(idx, 3, self.makePercentTableItem(self.curReport["data"][key]["statistics"]["numberOfHandsCorrect"], self.curReport["data"][key]["statistics"]["numberOfHands"]))
                self.table.setItem(idx, 4, self.makeTableItem(self.curReport["data"][key]["statistics"]["raiseNumberOfHands"]))
                self.table.setItem(idx, 5, self.makeTableItem(self.curReport["data"][key]["statistics"]["raiseNumberOfHandsCorrect"]))
                self.table.setItem(idx, 6, self.makePercentTableItem(self.curReport["data"][key]["statistics"]["raiseNumberOfHandsCorrect"], self.curReport["data"][key]["statistics"]["raiseNumberOfHands"]))
                self.table.setItem(idx, 7, self.makeTableItem(self.curReport["data"][key]["statistics"]["callNumberOfHands"]))
                self.table.setItem(idx, 8, self.makeTableItem(self.curReport["data"][key]["statistics"]["callNumberOfHandsCorrect"]))
                self.table.setItem(idx, 9, self.makePercentTableItem(self.curReport["data"][key]["statistics"]["callNumberOfHandsCorrect"], self.curReport["data"][key]["statistics"]["callNumberOfHands"]))
                self.table.setItem(idx, 10, self.makeTableItem(self.curReport["data"][key]["statistics"]["foldNumberOfHands"]))
                self.table.setItem(idx, 11, self.makeTableItem(self.curReport["data"][key]["statistics"]["foldNumberOfHandsCorrect"]))
                self.table.setItem(idx, 12, self.makePercentTableItem(self.curReport["data"][key]["statistics"]["foldNumberOfHandsCorrect"], self.curReport["data"][key]["statistics"]["foldNumberOfHands"]))

    def makePercentTableItem(self, num, dom):
        if dom == 0:
            return self.makeTableItem("N/A")
        else:
            return self.makeTableItem(num/dom)

    def makeTableItem(self, text):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def drawSpot(self, item):
        row = item.row()
        col = item.column()
        key = self.keyArr[row]
        # Get total and draw this
        if col < 4:
            total = self.curReport["data"][key]["handTotalArrAttempt"]    
            correct = self.curReport["data"][key]["handTotalArrCorrect"]    
            for i in range(13):
                for j in range(13):
                    self.buttonPushMap[i][j].updateButton(total[i][j], correct[i][j])
        # Get raise
        elif col >= 4 and col < 7:
            total = self.curReport["data"][key]["handRaiseArrAttempt"]    
            correct = self.curReport["data"][key]["handRaiseArrCorrect"]    
            for i in range(13):
                for j in range(13):
                    self.buttonPushMap[i][j].updateButton(total[i][j], correct[i][j])
        # Get Call
        elif col >= 7 and col < 10:
            total = self.curReport["data"][key]["handCallArrAttempt"]    
            correct = self.curReport["data"][key]["handCallArrCorrect"]    
            for i in range(13):
                for j in range(13):
                    self.buttonPushMap[i][j].updateButton(total[i][j], correct[i][j])
        # Get Fold
        else:
            total = self.curReport["data"][key]["handFoldArrAttempt"]    
            correct = self.curReport["data"][key]["handFoldArrCorrect"]    
            for i in range(13):
                for j in range(13):
                    self.buttonPushMap[i][j].updateButton(total[i][j], correct[i][j])
 
    def resetDraw(self):
        for i in range(13):
            for j in range(13):
                self.buttonPushMap[i][j].updateButton(0, 0)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                widget = child.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(child.layout())


