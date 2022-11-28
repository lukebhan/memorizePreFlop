from PyQt5.QtCore import Qt
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from customButton import DrawRangeButton
from functools import partial
from colorPicker import ColorButton
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
        self.raiseColor = "#90EE90"
        self.callColor = "#FFCCCB"
        self.main = mainWindow

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
        leftLayout = QHBoxLayout()
        leftLayout.setContentsMargins(70, 70, 70, 70)
        leftLayout.setSpacing(0)
        leftLayout.addLayout(self.buildButtonLayout())
        return leftLayout

    def buildRightLayout(self):
        rightLayout = QVBoxLayout()
        rightLayout.setContentsMargins(0,100, 0, 70)

        raiseButton, callButton = self.createRaiseCallButtons()
        raiseSlider, callSlider = self.createRaiseCallSliders()
        rightLayout.addLayout(raiseButton)
        rightLayout.addLayout(raiseSlider)
        rightLayout.addLayout(callButton)
        rightLayout.addLayout(callSlider)
        rightLayout.addLayout(self.createClearLoadSaveButtons())
        rightLayout.addLayout(self.createRangeBrowser())
        rightLayout.addLayout(self.createDependencyLabel())
        rightLayout.addLayout(self.createDependencyBrowser())
        return rightLayout

    def buildButtonLayout(self):
        buttonMainLayout = QHBoxLayout()
        buttonMainLayout.setSpacing(0)

        # Build out button matrix 
        self.firstButton = None
        for i in range(13):
            buttonSubLayout = QVBoxLayout()
            buttonArr = []
            for j in range(13):
                button = DrawRangeButton("#36454F", self.comboMap[i][j])
                button.setFont(self.font(30))
                buttonSubLayout.addWidget(button)
                button.clicked.connect(partial(self.fillButton, (button, [i,j])))
                buttonArr.append(button)
            buttonMainLayout.addLayout(buttonSubLayout)
            self.buttonPushMap.append(buttonArr)
        return buttonMainLayout
    
    def createRaiseCallButtons(self):
        # Values is 
        self.raiseCallButtonValue = 1

        raiseButtonLayout = QHBoxLayout()
        self.raiseColorButton = ColorButton(color="#90EE90", callbackFunc=self.updateRaiseColor)
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
        self.callColorButton = ColorButton(color="#FFCCCB", callbackFunc=self.updateCallColor)
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
        return raiseButtonLayout, callButtonLayout

    def updateCallValue(self):
        self.raiseCallButtonValue = 0
    
    def updateRaiseValue(self):
        self.raiseCallButtonValue = 1

    def updateCallColor(self):
        self.callColor = self.callColorButton.color()
        self.redrawAllButtons(self.callColor, 0)

    def updateRaiseColor(self):
        self.raiseColor = self.raiseColorButton.color()
        self.redrawAllButtons(self.raiseColor, 1)

    def createRaiseCallSliders(self):
        self.raiseSliderLabel = QLabel()
        self.callSliderLabel = QLabel()

        self.raiseSliderLabel.setText("0")
        self.callSliderLabel.setText("0")

        sliderRaise, self.raiseSlider = self.createSlider(self.raiseSliderLabel)
        sliderCall, self.callSlider = self.createSlider(self.callSliderLabel)

        self.raiseSlider.valueChanged.connect(self.raiseSliderLabel.setNum)
        self.callSlider.valueChanged.connect(self.callSliderLabel.setNum)
        return sliderRaise, sliderCall
    
    def createSlider(self, labelVar):
        sliderHBox = QHBoxLayout()
        sliderVBox = QVBoxLayout()

        sliderHBox.setContentsMargins(0, 0, 0, 0)
        sliderVBox.setContentsMargins(0, 0, 100, 0)

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
        return clearSaveLoadButtonLayout

    def createRangeBrowser(self):
        rangeEditLayout = QHBoxLayout()
        rangeEditLayout.setContentsMargins(0, 0, 40, 0)

        self.rangeLineEdit = QLineEdit()
        self.rangeLineEdit.setFont(self.font(8))
        self.rangeLineEdit.setText("ranges/")

        browseButton = QPushButton("Browse")
        browseButton.setFont(self.font(10))
        browseButton.clicked.connect(self.rangeBrowserButtonCallback)
        rangeEditLayout.addWidget(browseButton)
        rangeEditLayout.addWidget(self.rangeLineEdit)
        return rangeEditLayout

    def rangeBrowserButtonCallback(self):
        fileName, _ = QFileDialog().getOpenFileName(directory=os.getcwd()+"/ranges/")
        fileName = fileName[len(os.getcwd())+1:] 
        self.rangeLineEdit.setText(fileName)
        self.loadButtonCallback()
    
    def createDependencyLabel(self):
        dependencyLayout = QHBoxLayout()
        dependencyLayoutLabel = QLabel("Testing Hands to Include:")
        dependencyLayoutLabel.setFont(self.font(12))
        dependencyLayout.addWidget(dependencyLayoutLabel)
        return dependencyLayout
 
    def createDependencyBrowser(self):
        dependencyEditLayout = QHBoxLayout()
        dependencyEditLayout.setContentsMargins(0, 0, 40, 0)

        self.dependencyLineEdit = QLineEdit()
        self.dependencyLineEdit.setFont(self.font(8))
        self.dependencyLineEdit.setText("")

        browseButton = QPushButton("Browse")
        browseButton.setFont(self.font(10))
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
            QMessageBox.about(self.main, "Error", "File Format Invalid. Please Clear")

    def rangeDrawingToDict(self):
        dictionary = {}
        raiseArr = []
        callArr = []
        for idx, buttonArr in enumerate(self.buttonPushMap):
            for idx2, button in enumerate(buttonArr):
                raiseScale = button.getRaiseScale()
                callScale = button.getCallScale()
                hand = self.comboMap[idx][idx2]
                if raiseScale != 0:
                    raiseArr.append((hand, raiseScale))
                if callScale != 0:
                    callArr.append((hand, callScale))
        raiseArr = sorted(raiseArr, key=lambda x: -1*float(x[1]))
        callArr = sorted(callArr, key=lambda x: -1*float(x[1]))
        dictionary["raise"] = raiseArr
        dictionary["call"] = callArr
        return dictionary

    def dictToRangeDrawing(self, dictionary):
        raiseArr = dictionary["raise"]
        callArr = dictionary["call"]
        for val in raiseArr:
            i, j = self.comboMapInverse[val[0]]
            self.buttonPushMap[i][j].loadColorAndScale(self.raiseColor, val[1], 1)
        if callArr is not None:
            for val in callArr:
                i, j = self.comboMapInverse[val[0]]
                self.buttonPushMap[i][j].loadColorAndScale(self.callColor, val[1], 0)
        return True

    def parseFileToDictionary(self, filename):
        return parseLines(filename)

    def fillButton(self, button):
        # button contains the index that was pressed
        # button is of the form (button, [i, j])
        if self.raiseCallButtonValue == 1:
            button[0].changeColorAndScale(self.raiseColor, float(self.raiseSliderLabel.text())/100.0, 1)
        else:
            button[0].changeColorAndScale(self.callColor, float(self.callSliderLabel.text())/100.0, 0)

    def redrawAllButtons(self, color, raiseOrCall):
        for val in self.buttonPushMap:
            for val2 in val:
                val2.changeColor(color, raiseOrCall)


