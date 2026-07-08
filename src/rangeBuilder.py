from PyQt5.QtCore import Qt
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from customButton import DrawRangeButton
from functools import partial
from colorPicker import ColorButton
from dragWidget import DragWidget
from parser import *
import os

class RangeBuilder():
    def __init__(self, mainWindow, comboMap, comboMapInverse, font):
        self.generalTab = QWidget()
        self.mainLayout = QHBoxLayout()

        self.comboMap = comboMap
        self.comboMapInverse = comboMapInverse
        self.buttonPushMap = []
        # function for font building
        self.font = font
        self.callColor = "#90EE90"
        self.raiseColor = "#FFCCCB"
        self.allinColor = "#DDA0DD"
        self.main = mainWindow
        self.callVal = 0
        self.raiseVal = 0
        self.allinVal = 0
        self.xIdx = -1
        self.yIdx = -1

    def percentText(self):
        return ("Total: " + "{:.2f}".format((self.callVal + self.raiseVal + self.allinVal)/13.26) +
                " Raise: " + "{:.2f}".format(self.raiseVal/13.26) +
                " Call: " + "{:.2f}".format(self.callVal/13.26) +
                " All-In: " + "{:.2f}".format(self.allinVal/13.26) +
                " Fold: " + "{:.2f}".format((1326-self.callVal-self.raiseVal-self.allinVal)/13.26))

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
        leftLayout.setContentsMargins(20, 20, 20, 0)
        # Grid takes the stretch so it grows/shrinks with the window
        leftLayout.addWidget(self.buildButtonLayout(), 1)
        leftLayout.addLayout(self.buildPercentageLabelLayout())
        return leftLayout

    def buildRightLayout(self):
        rightLayout = QVBoxLayout()
        #rightLayout.setContentsMargins(0,100, 0, 70)

        raiseButton, callButton, allinButton = self.createRaiseCallButtons()
        raiseSlider, callSlider, allinSlider = self.createRaiseCallSliders()
        rightLayout.addLayout(raiseButton)
        rightLayout.addLayout(raiseSlider)
        rightLayout.addLayout(callButton)
        rightLayout.addLayout(callSlider)
        rightLayout.addLayout(allinButton)
        rightLayout.addLayout(allinSlider)
        rightLayout.addLayout(self.createClearLoadSaveButtons())
        rightLayout.addLayout(self.createRangeBrowser())
        rightLayout.addLayout(self.createDependencyLabel())
        rightLayout.addLayout(self.createDependencyBrowser())
        rightLayout.addStretch()
        return rightLayout

    def buildPercentageLabelLayout(self):
        self.percentLabel = QLabel(alignment=Qt.AlignLeft)
        self.percentLabel.setWordWrap(True)
        self.percentLabel.setMinimumWidth(0)
        self.percentLabel.setText(self.percentText())
        percentLabel = QHBoxLayout()
        percentLabel.addWidget(self.percentLabel)
        percentLabel.setContentsMargins(0, 20, 0, 0)
        return percentLabel

    def buildButtonLayout(self):
        buttonMainLayout = QHBoxLayout()
        buttonMainLayout.setSpacing(0)

        self.buttonWidget = DragWidget()
        self.buttonWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.buttonWidget.setLayout(buttonMainLayout)
        self.buttonWidget.drag.connect(self.addDragButton)

        # Build out button matrix 
        self.firstButton = None
        for i in range(13):
            buttonSubLayout = QVBoxLayout()
            buttonArr = []
            for j in range(13):
                button = DrawRangeButton("#36454F", self.comboMap[i][j])
                button.setFont(self.font(30))
                buttonSubLayout.addWidget(button)
                buttonArr.append(button)
                button.pressed.connect(partial(self.fillPressButton, (button, ([i, j]))))
            buttonMainLayout.addLayout(buttonSubLayout)
            self.buttonPushMap.append(buttonArr)
        return self.buttonWidget
    
    def createRaiseCallButtons(self):
        # Values is 
        self.raiseCallButtonValue = 1

        raiseButtonLayout = QHBoxLayout()
        self.raiseColorButton = ColorButton(color=self.raiseColor, callbackFunc=self.updateRaiseColor)
        raiseButton = QRadioButton(" Raise  ")
        raiseButton.setChecked(True)
        raiseButton.setFont(self.font(30))
        raiseButton.setStyleSheet("QRadioButton::indicator"
                                        "{"
                                        "width : 20px;"
                                        "height : 20px;"
                                        "}")
        raiseButton.toggled.connect(self.updateRaiseValue)
        raiseButtonLayout.addWidget(raiseButton, 0)
        raiseButtonLayout.addWidget(self.raiseColorButton, 0)
        raiseButtonLayout.addWidget(QLabel("  "))
    
        callButtonLayout = QHBoxLayout()
        self.callColorButton = ColorButton(color=self.callColor, callbackFunc=self.updateCallColor)
        callButton = QRadioButton(" Call   ")
        callButton.setStyleSheet("QRadioButton::indicator"
                                        "{"
                                        "width : 20px;"
                                        "height : 20px;"
                                        "}")
        callButton.setFont(self.font(30))
        callButton.toggled.connect(self.updateCallValue)
        callButtonLayout.addWidget(callButton, 0)
        callButtonLayout.addWidget(self.callColorButton, 0)
        callButtonLayout.addWidget(QLabel("  "))

        allinButtonLayout = QHBoxLayout()
        self.allinColorButton = ColorButton(color=self.allinColor, callbackFunc=self.updateAllinColor)
        allinButton = QRadioButton(" Raise All-In ")
        allinButton.setStyleSheet("QRadioButton::indicator"
                                        "{"
                                        "width : 20px;"
                                        "height : 20px;"
                                        "}")
        allinButton.setFont(self.font(30))
        allinButton.toggled.connect(self.updateAllinValue)
        allinButtonLayout.addWidget(allinButton, 0)
        allinButtonLayout.addWidget(self.allinColorButton, 0)
        allinButtonLayout.addWidget(QLabel("  "))
        return raiseButtonLayout, callButtonLayout, allinButtonLayout

    def updateCallValue(self):
        self.raiseCallButtonValue = 0

    def updateRaiseValue(self):
        self.raiseCallButtonValue = 1

    def updateAllinValue(self):
        self.raiseCallButtonValue = 2

    def updateCallColor(self):
        self.callColor = self.callColorButton.color()
        self.redrawAllButtons(self.callColor, 0)

    def updateRaiseColor(self):
        self.raiseColor = self.raiseColorButton.color()
        self.redrawAllButtons(self.raiseColor, 1)

    def updateAllinColor(self):
        self.allinColor = self.allinColorButton.color()
        self.redrawAllButtons(self.allinColor, 2)

    def createRaiseCallSliders(self):
        self.raiseSliderLabel = QLabel()
        self.callSliderLabel = QLabel()
        self.allinSliderLabel = QLabel()

        self.raiseSliderLabel.setText("0")
        self.callSliderLabel.setText("0")
        self.allinSliderLabel.setText("0")

        sliderRaise, self.raiseSlider = self.createSlider(self.raiseSliderLabel)
        sliderCall, self.callSlider = self.createSlider(self.callSliderLabel)
        sliderAllin, self.allinSlider = self.createSlider(self.allinSliderLabel)

        self.raiseSlider.valueChanged.connect(self.raiseSliderLabel.setNum)
        self.callSlider.valueChanged.connect(self.callSliderLabel.setNum)
        self.allinSlider.valueChanged.connect(self.allinSliderLabel.setNum)
        return sliderRaise, sliderCall, sliderAllin
    
    def createSlider(self, labelVar):
        sliderHBox = QHBoxLayout()
        sliderVBox = QVBoxLayout()

        sliderHBox.setContentsMargins(0, 0, 0, 0)
        sliderVBox.setContentsMargins(0, 0, 10, 0)

        label_min = QLabel("0", alignment=Qt.AlignLeft)
        label_max = QLabel("100", alignment=Qt.AlignRight)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setTickPosition(QSlider.TicksBelow)
        label_min.setFont(self.font(20))
        label_max.setFont(self.font(20))
        labelVar.setFont(self.font(20))
        sliderHBox.addWidget(label_min, Qt.AlignLeft)
        sliderHBox.addWidget(label_max, Qt.AlignRight)
        sliderVBox.addWidget(labelVar, Qt.AlignCenter)
        sliderVBox.addWidget(slider)
        sliderVBox.addLayout(sliderHBox)
        return sliderVBox, slider

    def createClearLoadSaveButtons(self):
        clearButton = QPushButton("Clear")
        loadButton = QPushButton("Load")
        saveButton = QPushButton("Save")
        clearButton.clicked.connect(self.clear)
        loadButton.clicked.connect(self.loadButtonCallback)
        saveButton.clicked.connect(self.saveButtonCallback)
        clearSaveLoadButtonLayout = QHBoxLayout()
        clearSaveLoadButtonLayout.addWidget(clearButton)
        clearSaveLoadButtonLayout.addWidget(saveButton)
        clearSaveLoadButtonLayout.addWidget(loadButton)
        clearSaveLoadButtonLayout.setContentsMargins(0, 40, 20, 20)
        return clearSaveLoadButtonLayout

    def createRangeBrowser(self):
        rangeEditLayout = QHBoxLayout()

        self.rangeLineEdit = QLineEdit()
        self.rangeLineEdit.setFont(self.font(10))
        self.rangeLineEdit.setText("ranges/")

        browseButton = QPushButton("Browse")
        browseButton.setFont(self.font(14))
        browseButton.clicked.connect(self.rangeBrowserButtonCallback)
        rangeEditLayout.addWidget(browseButton)
        rangeEditLayout.addWidget(self.rangeLineEdit)
        rangeEditLayout.setContentsMargins(0, 0, 20, 20)
        return rangeEditLayout

    def rangeBrowserButtonCallback(self):
        fileName, _ = QFileDialog().getOpenFileName(directory=os.getcwd()+"/ranges/")
        fileName = fileName[len(os.getcwd())+1:] 
        self.rangeLineEdit.setText(fileName)
        self.loadButtonCallback()
    
    def createDependencyLabel(self):
        dependencyLayout = QHBoxLayout()
        dependencyLayoutLabel = QLabel("Testing Hands to Include:")
        dependencyLayoutLabel.setFont(self.font(20))
        dependencyLayout.addWidget(dependencyLayoutLabel)
        return dependencyLayout
 
    def createDependencyBrowser(self):
        dependencyEditLayout = QHBoxLayout()
        dependencyEditLayout.setContentsMargins(0, 0, 20, 0)

        self.dependencyLineEdit = QLineEdit()
        self.dependencyLineEdit.setFont(self.font(10))
        self.dependencyLineEdit.setText("")

        browseButton = QPushButton("Browse")
        browseButton.setFont(self.font(14))
        browseButton.clicked.connect(self.dependencyBrowserButtonCallback)

        dependencyEditLayout.addWidget(browseButton)
        dependencyEditLayout.addWidget(self.dependencyLineEdit)
        return dependencyEditLayout

    def dependencyBrowserButtonCallback(self):
        fileName, _ = QFileDialog().getOpenFileName(directory=os.getcwd()+"/ranges/")
        fileName = fileName[len(os.getcwd())+1:] 
        self.dependencyLineEdit.setText(fileName)

    def createClearSaveLoadButtons(self):
        clearButton = QPushButton("Clear")
        loadButton = QPushButton("Load")
        saveButton = QPushButton("Save")

        clearButton.clicked.connect(self.clear)
        loadButton.clicked.connect(self.loadButtonCallback)
        saveButton.clicked.connect(self.saveButtonCallback)

        clearSaveLoadLayout = QHBoxLayout()
        clearSaveLoadLayout.addWidget(clearButton)
        clearSaveLoadLayout.addWidget(saveButton)
        clearSaveLoadLayout.addWidget(loadButton)
        clearSaveLoadLayout.setContentsMargins(0, 10, 40, 0)
        return clearSaveLoadLayout

    def clear(self):
        self.raiseVal = 0
        self.callVal = 0
        self.allinVal = 0
        self.percentLabel.setText(self.percentText())
        for buttonArr in self.buttonPushMap:
            for button in buttonArr:
                button.clear()

    def saveButtonCallback(self):
        dictionary = self.rangeDrawingToDict()
        filename = self.rangeLineEdit.text()
        filename = "./" + filename
        if self.dependencyLineEdit.text() == "":
            success = parseDictionaryToFile(filename, dictionary)
        else:
            success = parseDictionaryToFile(filename, dictionary, self.dependencyLineEdit.text())
        if not success:
            QMessageBox.about(self.main, "Error", "Unable to Save to File")
        else:
            QMessageBox.about(self.main, "Success", "File Saved Successfully!")

    def loadButtonCallback(self):
        self.clear()
        filename = self.rangeLineEdit.text()
        filename = "./" + filename
        dictionary, success = self.parseFileToDictionary(filename)
        if success == False:
            QMessageBox.about(self.main, "Error", dictionary)
            return
        success = self.dictToRangeDrawing(dictionary)
        if success == False:
            QMessageBox.about(self.main, "Error", "File Format Invalid. Clearing")

    def rangeDrawingToDict(self):
        dictionary = {}
        raiseArr = []
        callArr = []
        allinArr = []
        for idx, buttonArr in enumerate(self.buttonPushMap):
            for idx2, button in enumerate(buttonArr):
                raiseScale = button.getRaiseScale()
                callScale = button.getCallScale()
                allinScale = button.getAllinScale()
                hand = self.comboMap[idx][idx2]
                if raiseScale != 0:
                    raiseArr.append((hand, raiseScale))
                if callScale != 0:
                    callArr.append((hand, callScale))
                if allinScale != 0:
                    allinArr.append((hand, allinScale))
        raiseArr = sorted(raiseArr, key=lambda x: -1*float(x[1]))
        callArr = sorted(callArr, key=lambda x: -1*float(x[1]))
        allinArr = sorted(allinArr, key=lambda x: -1*float(x[1]))
        dictionary["raise"] = raiseArr
        dictionary["call"] = callArr
        dictionary["allin"] = allinArr
        return dictionary

    def dictToRangeDrawing(self, dictionary):
        raiseArr = dictionary["raise"]
        callArr = dictionary["call"]
        allinArr = dictionary.get("allin", [])
        for val in raiseArr:
            i, j = self.comboMapInverse[val[0]]
            self.buttonPushMap[i][j].loadColorAndScale(self.raiseColor, val[1], 1)
        if callArr is not None:
            for val in callArr:
                i, j = self.comboMapInverse[val[0]]
                self.buttonPushMap[i][j].loadColorAndScale(self.callColor, val[1], 0)
        if allinArr is not None:
            for val in allinArr:
                i, j = self.comboMapInverse[val[0]]
                self.buttonPushMap[i][j].loadColorAndScale(self.allinColor, val[1], 2)
        return True

    def parseFileToDictionary(self, filename):
        return parseLines(filename)

    def addDragButton(self, position):
        widthRatio = self.buttonWidget.width()/13.0
        heightRatio = self.buttonWidget.height()/13.0
        xIdx = int(position.x()/widthRatio)
        yIdx = int(position.y()/heightRatio)
        if xIdx != self.xIdx or yIdx != self.yIdx:
            if xIdx < 13 and xIdx > -1 and yIdx < 13 and yIdx > -1:
                self.xIdx = xIdx
                self.yIdx = yIdx
                self.fillButton((self.buttonPushMap[xIdx][yIdx], [xIdx, yIdx]))

    def fillPressButton(self, button):
        self.xIdx = button[1][0]
        self.yIdx = button[1][1]
        self.fillButton(button)

    def fillButton(self, button):
        # button contains the index that was pressed
        # button is of the form (button, [i, j])
        # Number of combos represented by this cell: offsuit=4, suited=12, pair=6
        if button[1][0] > button[1][1]:
            mult = 4
        elif button[1][0] < button[1][1]:
            mult = 12
        else:
            mult = 6

        if self.raiseCallButtonValue == 1:
            curValue = button[0].getRaiseScale()
            self.raiseVal -= curValue*mult
            button[0].changeColorAndScale(self.raiseColor, float(self.raiseSliderLabel.text())/100.0, 1)
            self.raiseVal += button[0].getRaiseScale()*mult
        elif self.raiseCallButtonValue == 2:
            curValue = button[0].getAllinScale()
            self.allinVal -= curValue*mult
            button[0].changeColorAndScale(self.allinColor, float(self.allinSliderLabel.text())/100.0, 2)
            self.allinVal += button[0].getAllinScale()*mult
        else:
            curValue = button[0].getCallScale()
            self.callVal -= curValue*mult
            button[0].changeColorAndScale(self.callColor, float(self.callSliderLabel.text())/100.0, 0)
            self.callVal += button[0].getCallScale()*mult

        self.percentLabel.setText(self.percentText())


    def redrawAllButtons(self, color, raiseOrCall):
        for val in self.buttonPushMap:
            for val2 in val:
                val2.changeColor(color, raiseOrCall)
