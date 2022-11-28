from PyQt5.QtCore import Qt
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from customButton import DrawRangeButton
from customButton import DrawScenarioButton
from functools import partial
from colorPicker import ColorButton
from parser import *
import os
from glob import glob
import numpy as np

class ChartTrainer():
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
        self.sceneDict = {}
        self.curSelection = None
        self.tol = 0.05
        self.score = "Score: "

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

        self.leftLeftLayout = QVBoxLayout()
        self.leftRightLayout = QVBoxLayout()
        # This must be split into two portions. 
        
        self.leftLeftLayout.setContentsMargins(70, 0, 50, 0)
        self.leftLeftLayout.setSpacing(0)

        self.leftRightLayout.setContentsMargins(0, 100, 50, 100)

        self.dynamicCheckLayout = QHBoxLayout()
        #self.dynamicCheckLayout.setContentsMargins(0, 20, 20, 20)
        self.leftRightLayout.addLayout(self.dynamicCheckLayout)

        leftLayout.addLayout(self.leftLeftLayout)
        leftLayout.addLayout(self.leftRightLayout)

        return leftLayout

    def addLeftLayoutComponents(self):
        self.leftLeftLayout.addLayout(self.createProblemLabel())
        self.leftLeftLayout.addLayout(self.buildButtonLayout())

        self.dynamicCheckLayout.addLayout(self.createCheckButton())
        raiseButton, callButton = self.createRaiseCallButtons()
        raiseSlider, callSlider = self.createRaiseCallSliders()

        self.leftRightLayout.addLayout(self.createScoreLabel())
        self.leftRightLayout.addLayout(raiseButton)
        self.leftRightLayout.addLayout(raiseSlider)
        self.leftRightLayout.addLayout(callButton)
        self.leftRightLayout.addLayout(callSlider)

        self.leftRightLayout.addLayout(self.dynamicCheckLayout)


    def buildRightLayout(self):
        rightLayout = QVBoxLayout()
        rightLayout.setContentsMargins(0,100, 70, 70)
        rightLayout.addLayout(self.createResetAndStartButtons())
        rightLayout.addLayout(self.createAddDeleteClearButtons())
        rightLayout.addLayout(self.createRangeBrowser())
        rightLayout.addWidget(self.createActiveScenariosListing())

        return rightLayout

    def buildButtonLayout(self):
        buttonMainLayout = QHBoxLayout()

        # Build out button matrix 
        self.firstButton = None
        for i in range(13):
            buttonSubLayout = QVBoxLayout()
            buttonArr = []
            for j in range(13):
                button = DrawRangeButton("#36454F", self.comboMap[i][j])
                button.setFont(self.font(16))
                buttonSubLayout.addWidget(button)
                button.clicked.connect(partial(self.fillButton, (button, [i,j])))
                buttonArr.append(button)
            buttonSubLayout.addStretch()
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

    def clear(self):
        for buttonArr in self.buttonPushMap:
            for button in buttonArr:
                button.clear()

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


    def createScoreLabel(self):
        scoreLayout = QHBoxLayout()
        self.scoreLabel = QLabel(self.score)
        scoreLayout.addWidget(self.scoreLabel)
        scoreLayout.setContentsMargins(0, 0, 20,20)
        return scoreLayout

    def createCheckButton(self):
        checkButtonLayout = QHBoxLayout()
        checkButton = QPushButton("Check")
        checkButton.clicked.connect(self.checkScenarioCallback)
        checkButtonLayout.addWidget(checkButton)
        checkButton.setFont(self.font(18))
        return checkButtonLayout
    
    def checkScenarioCallback(self):
        correct = self.drawIncorrectValues()
        # First score
        if self.scoreLabel.text() == "Score: ":
            if correct:
                self.score = ("Score: 1/1")
            else:
                self.score = ("Score: 0/1")
        else:
            num, dom = self.parseScore()
            if correct:
                self.score = "Score: " + str(int(num)+1) + "/" + str(int(dom)+1)
            else:
                self.score = "Score: " + str(int(num)) + "/" + str(int(dom)+1)
        self.clearLayout(self.dynamicCheckLayout)
        self.dynamicCheckLayout.addLayout(self.createShowAndNextButtons())
    
    def parseScore(self):
        score = self.scoreLabel.text()
        score = score[7:]
        score = score.split("/")
        return float(score[0]), float(score[1])

    def drawIncorrectValues(self):
        correctDictionary = self.sceneDict[self.problemLabel]
        correctDictionaryRaise = dict(correctDictionary["raise"])
        correctDictionaryCall = dict(correctDictionary["call"])
        correct=True
        for idx, buttonArr in enumerate(self.buttonPushMap):
            for idx2, button in enumerate(buttonArr):
                raiseScale = button.getRaiseScale()
                callScale = button.getCallScale()
                hand = self.comboMap[idx][idx2]
                print(hand)
                if hand in correctDictionaryRaise:
                    correctScale = correctDictionaryRaise[hand]
                    if raiseScale > correctScale + self.tol or raiseScale < correctScale -self.tol:
                        button.markIncorrect()
                        correct=False
                        continue
                else:
                    if raiseScale > self.tol:
                        button.markIncorrect()
                        correct=False
                        continue
                if hand in correctDictionaryCall:
                    correctScale = correctDictionaryCall[hand]
                    if callScale > correctScale + self.tol or callScale < correctScale - self.tol:
                        button.markIncorrect()
                        correct=False
                        continue
                else:
                    if callScale > self.tol:
                        button.markIncorrect()
                        correct=False
                        continue
        return correct

    def createShowAndNextButtons(self):
        showAndNextButtonLayout = QHBoxLayout()
        showSolutionButton = QPushButton("Show solution")
        showSolutionButton.clicked.connect(self.showSolutionCallback)
        showSolutionButton.setFont(self.font(18))
        nextButton = QPushButton("Next")
        nextButton.clicked.connect(self.nextCallback)
        nextButton.setFont(self.font(18))
        showAndNextButtonLayout.addWidget(showSolutionButton, Qt.AlignLeft)
        showAndNextButtonLayout.addWidget(nextButton, Qt.AlignLeft)
        return showAndNextButtonLayout

    def showSolutionCallback(self):
        for val in self.buttonPushMap:
            for val2 in val:
                val2.markCorrect()
        self.dictToRangeDrawing(self.sceneDict[self.problemLabel])

    def nextCallback(self):
        self.generateTrainingScenario()

    def createProblemLabel(self):
        problemLayout = QHBoxLayout()
        self.curProblemName = QLabel()
        self.curProblemName.setAlignment(Qt.AlignCenter)
        problemLayout.addWidget(self.curProblemName)
        problemLayout.setContentsMargins(0, 35, 0, 50)
        return problemLayout


    # Start Right Layout Components

    def createResetAndStartButtons(self):
        resetStartButtonLayout = QHBoxLayout()
        resetButton = QPushButton("Reset")
        resetButton.clicked.connect(self.resetTrainingScene)
        startButton = QPushButton("Start Training")
        startButton.clicked.connect(self.startTrainingScene)

        resetStartButtonLayout.addWidget(startButton)
        resetStartButtonLayout.addWidget(resetButton)
        resetStartButtonLayout.setContentsMargins(0, 0, 0, 20)

        return resetStartButtonLayout

    def resetTrainingScene(self):
        self.clearScenario()
        if len(self.sceneDict) > 0:
            self.scoreLabel = QLabel()

    def startTrainingScene(self):
        self.resetTrainingScene()
        self.score = "Score: "
        if len(self.sceneDict) > 0:
            self.generateTrainingScenario()
        else:
            QMessageBox.about(self.main, "Error", "Cannot Start a Training Without any Scenarios Loaded")

    def createAddDeleteClearButtons(self):
        addButton = QPushButton("Add")
        addButton.clicked.connect(self.addScenes)

        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.deleteScene)

        clearButton = QPushButton("Clear")
        clearButton.clicked.connect(self.clearScene)

        addDeleteClearButtonLayout = QHBoxLayout()
        addDeleteClearButtonLayout.addWidget(addButton)
        addDeleteClearButtonLayout.addWidget(deleteButton)
        addDeleteClearButtonLayout.addWidget(clearButton)
        addDeleteClearButtonLayout.setContentsMargins(0, 0, 0, 20)
        return addDeleteClearButtonLayout

    def addScenes(self):
        path = self.sceneLineEdit.text()
        isExist = os.path.exists(path)
        if isExist:
            # add all scenarios in dir. Include sub directorys
            if os.path.isdir(path):
                result = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.txt'))]
                for val in result:
                    self.addScene(val)
            else:
                self.addScene(path)
        else:
            QMessageBox.about(self.main, "Error", "Scenario " + path + " File Not Found")

    def addScene(self, path):
        if path not in self.sceneDict.keys():
            sceneDict, success = parseLines(path)
            if not success:
                QMessageBox.about(self.main, "Error", "For scenario \"" + path +"\" " + sceneDict)
                return
            else:
                self.sceneDict[path] = sceneDict
            button = DrawScenarioButton(path)
            button.setFont(self.font(15))
            button.clicked.connect(partial(self.selectScenario, (button)))
            self.dynamicScenarioLayout.addWidget(button)
        else:
            QMessageBox.about(self.main, "Error", "Scenario \""+ path + "\" Already Added")

    def selectScenario(self, button):
        if self.curSelection == None:
            button.updateSelected()
            self.curSelection = button
        else:
            self.curSelection.updateSelected()
            self.curSelection = button
            button.updateSelected()

    def deleteScene(self):
        if self.curSelection is not None:
            self.sceneDict.pop(self.curSelection.textVal)
            if self.curSelection.textVal == self.problemLabel:
                # Make new scenario if available
                if len(self.sceneDict) != 0:
                    self.generateTrainingScenario()
            self.curSelection.deleteLater()
            self.curSelection = None

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                widget = child.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(child.layout())

    def clearScene(self):
        self.clearLayout(self.dynamicScenarioLayout)
        self.sceneDict = {}
        self.curSelection = None

    def createRangeBrowser(self):
        rangeBrowserLayout = QHBoxLayout()
        rangeBrowserLayout.setContentsMargins(0, 0, 40, 0)

        browseButton = QPushButton("Browse")
        browseButton.setFont(self.font(12))
        browseButton.clicked.connect(self.rangeBrowseButtonCallback)

        self.sceneLineEdit = QLineEdit()
        self.sceneLineEdit.setFont(self.font(10))
        self.sceneLineEdit.setText("ranges/")

        rangeBrowserLayout.addWidget(browseButton)
        rangeBrowserLayout.addWidget(self.sceneLineEdit)
        return rangeBrowserLayout

    def rangeBrowseButtonCallback(self):
        fileName, _ = QFileDialog().getOpenFileNames(directory=os.getcwd()+"/ranges/")
        if len(fileName) > 1:
            for val in fileName:
                val= val[len(os.getcwd())+1:] 
                self.addScene(val)
        elif len(fileName) > 0:
            fileName = fileName[0][len(os.getcwd())+1:] 
            self.sceneLineEdit.setText(fileName)
            self.addScene(fileName)

    def createActiveScenariosLabel(self):
        activeScenariosLabel = QLabel("Active Scenarios")
        return activeScenariosLabel

    def createActiveScenariosListing(self):
        activeScenariosListing = QScrollArea()
        activeScenariosListing.setAlignment(Qt.AlignTop)
    
        # trick to insert dynamically. probs better way to do this
        widget = QWidget()
        activeScenariosListing.setWidgetResizable(True)
        activeScenariosListing.setWidget(widget)

        self.dynamicScenarioLayout = QVBoxLayout()
        self.dynamicScenarioLayout.setSpacing(5)
        widget.setLayout(self.dynamicScenarioLayout)
        return activeScenariosListing

    def generateTrainingScenario(self):
        self.clearScenario()
        self.addLeftLayoutComponents()
        self.updateScenarioProblem()

    def updateScenarioProblem(self):
        problemVal = np.random.randint(0, len(self.sceneDict))
        self.problemLabel = list(self.sceneDict.keys())[problemVal]
        splitName = self.problemLabel.split("/")
        splitName = splitName[-1].split(".")
        splitName = splitName[0].split("_")
        res = ""
        for val in splitName:
            res += val +" "
        self.curProblemName.setText("Spot: " + res)

    def clearScenario(self):
        self.buttonPushMap = []
        self.clearLayout(self.leftLeftLayout)
        self.clearLayout(self.leftRightLayout)


