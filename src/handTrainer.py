from PyQt5.QtCore import Qt
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
from glob import glob
from parser import *
from customButton import DrawScenarioButton
from functools import partial
import numpy as np

class HandTrainer():
    def __init__(self, main, comboMap, font, report=None):
        self.generalTab = QWidget()
        self.mainLayout = QHBoxLayout()

        self.main = main
        self.font = font
        self.comboMap = comboMap
        self.sceneIsClear = True
        self.sceneDict = {}
        self.curSelection = None
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
        leftLayout = QHBoxLayout()
        leftLayout.setContentsMargins(70, 20, 70, 70)
        leftLayout.setSpacing(0)
       
        self.leftTrainerLayout = QVBoxLayout()
        self.leftTrainerLayout.stretch(0)

        leftLayout.addLayout(self.leftTrainerLayout)

        return leftLayout

    def buildRightLayout(self):
        rightLayout = QVBoxLayout()
        #rightLayout.setContentsMargins(0, 100, 70, 70)
        rightLayout.addWidget(self.trainingActive())
        rightLayout.addLayout(self.createResetAndStartButtons())
        rightLayout.addLayout(self.createAddDeleteClearButtons())
        rightLayout.addLayout(self.createRangeBrowser())
        rightLayout.addWidget(self.createActiveScenariosListing())
        return rightLayout

    def trainingActive(self):
        self.trainingLabel = QLabel()
        self.trainingLabel.setFont(self.font(15))
        if self.report.isActive():
            self.trainingLabel.setText("Reporting Active")
            self.trainingLabel.setStyleSheet('color: green')
        else:
            self.trainingLabel.setText("Reporting Inactive")
            self.trainingLabel.setStyleSheet('color: red')
        return self.trainingLabel

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
        if len(self.sceneDict) > 0:
            self.scoreLabel = QLabel()
            self.clearTrainingScenario()

    def startTrainingScene(self):
        self.resetTrainingScene()
        if len(self.sceneDict) > 0:
            self.generateFirstTrainingScene()
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
        if self.sceneIsClear:
            # generate first training scene
            self.generateFirstTrainingScene()

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
                self.clearTrainingScenario()
                # Make new scenario if available
                if len(self.sceneDict) != 0:
                    self.generateFirstTrainingScene()
            self.curSelection.deleteLater()
            self.curSelection = None

    def clearScene(self):
        self.clearTrainingScenario()
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

    # Game Dynamics Section.
    def generateFirstTrainingScene(self): 
        self.sceneIsClear = False
        sceneLayout = QVBoxLayout()
        sceneLayout.addWidget(self.createSceneProblemTitle())
        sceneLayout.addLayout(self.createMainSceneComponents())
        sceneLayout.addLayout(self.createSceneButtons())
        self.leftTrainerLayout.addLayout(sceneLayout)
        self.generateTrainingScenario()

    def createSceneProblemTitle(self):
        # needs to be self because this is modified 
        self.curProblemName  = QLabel()
        self.curProblemName.setAlignment(QtCore.Qt.AlignCenter)
        self.curProblemName.setFont(self.font(36))
        return self.curProblemName

    def createMainSceneComponents(self):
        # includes randomizer, cards and score
        mainScene = QHBoxLayout()
        mainScene.stretch(1)
        mainScene.addWidget(self.createSceneRandomizer())
        mainScene.addLayout(self.createSceneCards())
        mainScene.addWidget(self.createSceneScore())
        return mainScene

    def createSceneCards(self):
        cardLayout = QHBoxLayout()
        cardLayout.setContentsMargins(50, 0, 50, 50)
        # dynamic labels which will be card images
        self.card1 = QLabel()
        self.card2 = QLabel()
        cardLayout.addWidget(self.card1)
        cardLayout.addWidget(self.card2)
        cardLayout.setSpacing(30)
        # need to store. This height width will be immutable
        self.cardHeight = self.card1.height()
        self.cardWidth = self.card1.width()
        return cardLayout

    def createSceneRandomizer(self):
        # will store randomizer value
        self.randomLabel = QLabel()
        return self.randomLabel

    def createSceneScore(self):
        # will store current score
        self.scoreLabel = QLabel()
        return self.scoreLabel
    
    def createSceneButtons(self):
        self.sceneButtonLayout = QHBoxLayout()
        callButton = QPushButton("Call")
        raiseButton = QPushButton("Raise")
        foldButton = QPushButton("Fold")

        callButton.clicked.connect(self.scenarioCallButtonCallback)
        raiseButton.clicked.connect(self.scenarioRaiseButtonCallback)
        foldButton.clicked.connect(self.scenarioFoldButtonCallback)
        self.sceneButtonLayout.addWidget(raiseButton)
        self.sceneButtonLayout.addWidget(callButton)
        self.sceneButtonLayout.addWidget(foldButton)

    def scenarioRaiseButtonCallback(self):
        raiseWeight, callWeight, foldWeight = self.getWeights()
        if float(self.randomInt) / 100.0 >= callWeight+foldWeight:
            if self.report.isActive():
                self.report.addHandData(self.res, self.hand, True, 1, True)
            if self.scoreLabel.text() == "":
                self.scoreLabel.setText("Score: 1/1")
            else:
                num, dom = self.parseScore()
                self.scoreLabel.setText("Score: " + str(int(num)+1) + "/" + str(int(dom)+1))
            self.generateTrainingScenario()
        else:
            if self.report.isActive():
                self.report.addHandData(self.res, self.hand, False, 1, True)
            if self.scoreLabel.text() == "":
                self.scoreLabel.setText("Score: 0/1")
            else:
                num, dom = self.parseScore()
                self.scoreLabel.setText("Score: " + str(int(num)) + "/" + str(int(dom)+1))
            self.clearLayout(self.sceneButtonLayout)
            self.buildDisplayWeights(raiseWeight, callWeight, foldWeight)
            
    def scenarioCallButtonCallback(self):
        raiseWeight, callWeight, foldWeight = self.getWeights()
        if float(self.randomInt) / 100.0 >= foldWeight and self.randomInt/100 < (callWeight+foldWeight):
            if self.report.isActive():
                self.report.addHandData(self.res, self.hand, True, 2, True)
            if self.scoreLabel.text() == "":
                self.scoreLabel.setText("Score: 1/1")
            else:
                num, dom = self.parseScore()
                self.scoreLabel.setText("Score: " + str(int(num)+1) + "/" + str(int(dom)+1))
            self.generateTrainingScenario()
        else:
            if self.report.isActive():
                self.report.addHandData(self.res, self.hand, False, 2, True)
            if self.scoreLabel.text() == "":
                self.scoreLabel.setText("Score: 0/1")
            else:
                num, dom = self.parseScore()
                self.scoreLabel.setText("Score: " + str(int(num)) + "/" + str(int(dom)+1))
            self.clearLayout(self.sceneButtonLayout)
            self.buildDisplayWeights(raiseWeight, callWeight, foldWeight)

    def scenarioFoldButtonCallback(self):
        raiseWeight, callWeight, foldWeight = self.getWeights()
        if float(self.randomInt) / 100.0 < foldWeight:
            if self.report.isActive():
                self.report.addHandData(self.res, self.hand, True, 3, True)
            if self.scoreLabel.text() == "":
                self.scoreLabel.setText("Score: 1/1")
            else:
                num, dom = self.parseScore()
                self.scoreLabel.setText("Score: " + str(int(num)+1) + "/" + str(int(dom)+1))
            self.generateTrainingScenario()
        else:
            if self.report.isActive():
                self.report.addHandData(self.res, self.hand, False, 3, True)
            if self.scoreLabel.text() == "":
                self.scoreLabel.setText("Score: 0/1")
            else:
                num, dom = self.parseScore()
                self.scoreLabel.setText("Score: " + str(int(num)) + "/" + str(int(dom)+1))
            self.clearLayout(self.sceneButtonLayout)
            self.buildDisplayWeights(raiseWeight, callWeight, foldWeight)

    def parseScore(self):
        score = self.scoreLabel.text()
        score = score[7:]
        score = score.split("/")
        s1 = float(score[0])
        s2 = float(score[1])
        if s1 > 9 or s2 > 9:
            self.scoreLabel.setFont(self.font(19))
        if s1 > 99 or s2 > 99:
            self.scoreLabel.setFont(self.font(17))
        return s1, s2

    def buildDisplayWeights(self, raiseWeight, callWeight, foldWeight):
        layout = QHBoxLayout()
        layoutLabel = QHBoxLayout()
        layoutLabel.setSpacing(2)
        layoutLabel.setContentsMargins(0, 0, 10, 0)

        incLabel = QLabel("Incorrect  ")
        incLabel.setFont(self.font(15))

        raiseLabel = QLabel("Raise Weight: " + str(raiseWeight) + "  ")
        raiseLabel.setStyleSheet("color: green")
        raiseLabel.setFont(self.font(15))

        callLabel = QLabel("Call Weight: " + str(callWeight) +"  ")
        callLabel.setStyleSheet("color: blue")
        callLabel.setFont(self.font(15))

        foldLabel = QLabel("Fold Weight: " + str(foldWeight) + "  ")
        foldLabel.setStyleSheet("color: red")
        foldLabel.setFont(self.font(15))

        layoutLabel.addWidget(incLabel)
        layoutLabel.addWidget(raiseLabel)
        layoutLabel.addWidget(callLabel)
        layoutLabel.addWidget(foldLabel)

        continueButton = QPushButton("Continue")
        continueButton.clicked.connect(self.generateTrainingScenario)
        layout.addLayout(layoutLabel)
        layout.addWidget(continueButton)
        self.sceneButtonLayout.addLayout(layout)

    def getWeights(self):
        weightDict = self.sceneDict[self.problemLabel]
        raiseWeight = 0
        callWeight = 0
        for val in weightDict["raise"]:
            if self.hand in val[0]:
                raiseWeight += float(val[1])
        if weightDict["call"] is not None:
            for val in weightDict["call"]:
                if self.hand in val[0]:
                    callWeight += float(val[1])
        return raiseWeight, callWeight, 1-raiseWeight-callWeight

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clearLayout(child.layout())

    def generateTrainingScenario(self):
        if self.report.isActive():
            self.trainingLabel.setText("Reporting Active")
            self.trainingLabel.setStyleSheet('color: green')
        else:
            self.trainingLabel.setText("Reporting Inactive")
            self.trainingLabel.setStyleSheet('color: red')
        self.clearLayout(self.sceneButtonLayout)
        self.createSceneButtons()
        self.leftTrainerLayout.addLayout(self.sceneButtonLayout)
        self.updateScenarioProblem()
        self.updateScenarioRandomizer()
        self.getHand()
        self.updateHandDrawing(int(self.cardWidth/2.8), int(self.cardHeight/1.55))

    def updateScenarioProblem(self):
        problemVal = np.random.randint(0, len(self.sceneDict))
        self.problemLabel = list(self.sceneDict.keys())[problemVal]
        splitName = self.problemLabel.split("/")
        splitName = splitName[-1].split(".")
        splitName = splitName[0].split("_")
        self.res = ""
        for val in splitName:
            self.res += val +" "
        self.curProblemName.setText("Spot: " + self.res)

    def updateScenarioRandomizer(self):
        self.randomInt = np.random.randint(0, 100)
        self.randomLabel.setText("Randomizer:\n    " + str(self.randomInt))

    def clearTrainingScenario(self):
        self.sceneIsClear = True
        self.clearLayout(self.leftTrainerLayout)

    def updateHandDrawing(self, cardWidth, cardHeight):
        pixmap = QPixmap(self.card1Path)
        pixmap = pixmap.scaled(cardWidth, cardHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.card1.setPixmap(pixmap)

        pixmap = QPixmap(self.card2Path)
        pixmap = pixmap.scaled(cardWidth, cardHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.card2.setPixmap(pixmap)

    def getHand(self):
        weightDict = self.sceneDict[self.problemLabel]
        hand = np.random.randint(0, 169)
        comboMap  =self.comboMap.reshape(169)
        self.hand = comboMap[hand]
        if "Depends" in weightDict:
            while self.hand not in weightDict["Depends"]:
                hand = np.random.randint(0, 169)
                comboMap  =self.comboMap.reshape(169)
                self.hand = comboMap[hand]
        if self.hand[-1] != "s":
            suit1 = np.random.randint(0, 4)
            suit2 = np.random.randint(0, 4)
            while suit2 == suit1:
                suit2 = np.random.randint(0, 4)
        else:
            suit1 = np.random.randint(0, 4)
            suit2 = suit1
        suits = ["clubs", "spades", "diamonds", "hearts"]
        self.card1Path = "./cardimages/" + str(self.hand[0] + suits[suit1])
        self.card2Path = "./cardimages/" + str(self.hand[1] + suits[suit2])
