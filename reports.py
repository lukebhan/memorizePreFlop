from PyQt5.QtCore import Qt
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from customButton import DrawReportButton
from functools import partial
from colorPicker import ColorButton
from parser import *
import os
import numpy as np

class Report():
    def __init__(self, comboMap, comboMapInverse, active):
        self.comboMap = comboMap
        self.comboMapInverse = comboMapInverse
        self.active = active
        self.report = {}
        self.generateReport("report1")

    def isActive(self):
        return self.active

    def setActive(self):
        self.active = True

    def setInactive(self):
        self.active = False

    def getReport(self):
        return self.report

    def generateReport(self, name):
        self.report["name"] = name
        self.report["data"] = {}
        self.generateSpot("Total")
        self.setActive()

    def generateSpot(self, spotName):
        spot = {}
        spot["handTotalArrAttempt"] = np.zeros((13, 13), dtype=np.int32)
        spot["handTotalArrCorrect"] = np.zeros((13, 13), dtype=np.int32)
        spot["handRaiseArrAttempt"] = np.zeros((13, 13), dtype=np.int32)
        spot["handRaiseArrCorrect"] = np.zeros((13, 13), dtype=np.int32)
        spot["handCallArrAttempt"] = np.zeros((13, 13), dtype=np.int32)
        spot["handCallArrCorrect"] = np.zeros((13, 13), dtype=np.int32)
        spot["handFoldArrAttempt"] = np.zeros((13, 13), dtype=np.int32)
        spot["handFoldArrCorrect"] = np.zeros((13, 13), dtype=np.int32)
        spot["chartTrainerArrAttempt"] = np.zeros((13, 13), dtype=np.int32)
        spot["chartTrainerArrCorrect"] = np.zeros((13, 13), dtype=np.int32)
        spot["statistics"] = {}
        spot["statistics"]["numberOfHands"] = 0
        spot["statistics"]["numberOfHandsCorrect"] = 0
        spot["statistics"]["raiseNumberOfHands"] = 0
        spot["statistics"]["raiseNumberOfHandsCorrect"] = 0
        spot["statistics"]["callNumberOfHands"] = 0
        spot["statistics"]["callNumberOfHandsCorrect"] = 0
        spot["statistics"]["foldNumberOfHands"] = 0
        spot["statistics"]["foldNumberOfHandsCorrect"] = 0
        self.report["data"][spotName] = spot

    def clearReport(self):
        self.report = {}

    def saveReport(self, filename):
        try:
            with open(filename, "w") as f:
                f.write(self.report["name"] +"\n")
                for spot in self.report["data"].keys():
                    f.write(spot + "\n")
                    spot = self.report["data"][spot]
                    f.write(str(spot["statistics"]["numberOfHands"]) +"\n")
                    f.write(str(spot["statistics"]["numberOfHandsCorrect"]) +"\n")
                    f.write(str(spot["statistics"]["raiseNumberOfHands"]) +"\n")
                    f.write(str(spot["statistics"]["raiseNumberOfHandsCorrect"]) +"\n")
                    f.write(str(spot["statistics"]["callNumberOfHands"]) +"\n")
                    f.write(str(spot["statistics"]["callNumberOfHandsCorrect"]) +"\n")
                    f.write(str(spot["statistics"]["foldNumberOfHands"]) +"\n")
                    f.write(str(spot["statistics"]["foldNumberOfHandsCorrect"]) +"\n")
                    self.writeArr(f, spot["handTotalArrAttempt"])
                    self.writeArr(f, spot["handTotalArrCorrect"])
                    self.writeArr(f, spot["handRaiseArrAttempt"])
                    self.writeArr(f, spot["handRaiseArrCorrect"])
                    self.writeArr(f, spot["handCallArrAttempt"])
                    self.writeArr(f, spot["handCallArrCorrect"])
                    self.writeArr(f, spot["handFoldArrAttempt"])
                    self.writeArr(f, spot["handFoldArrCorrect"])
            return True 
        except:
            return False

    def writeArr(self, f, arr):
        arr = arr.flatten()
        for i in range(len(arr)-1):
            f.write(str(arr[i]) + ",")
        f.write(str(arr[-1]) + "\n")

    def readArr(self, line):
        arr = np.zeros((169))
        line = line.split(",")
        for idx in range(168):
            arr[idx] = int(line[idx])
        arr[-1] = int(line[-1].rstrip())
        arr = arr.reshape((13, 13))
        return arr

    def loadReport(self, filename):
        self.clearReport()
        try:
            with open(filename, "r") as f:
                line = f.readline()
                self.report["name"] = line.rstrip()
                self.report["data"] = {}
                while line:
                    # line contains the next line after the spot once self.loadSpot is called
                    success, line, spotName, spot = self.loadSpot(f)
                    if success:
                        self.report["data"][spotName] = spot
            return True
        except:
            return False

    def loadSpot(self, f):
        line = f.readline()
        if not line:
            return False, None, None, None
        else:
            try:
                spotName = line.rstrip()
                spot = {}
                spot["statistics"] = {}
                line = f.readline()
                spot["statistics"]["numberOfHands"] = int(int(line.rstrip()))
                line = f.readline()
                spot["statistics"]["numberOfHandsCorrect"] = int(int(line.rstrip()))
                line = f.readline()
                spot["statistics"]["raiseNumberOfHands"] = int(int(line.rstrip()))
                line = f.readline()
                spot["statistics"]["raiseNumberOfHandsCorrect"] = int(line.rstrip())
                line = f.readline()
                spot["statistics"]["callNumberOfHands"] = int(line.rstrip())
                line = f.readline()
                spot["statistics"]["callNumberOfHandsCorrect"] = int(line.rstrip())
                line = f.readline()
                spot["statistics"]["foldNumberOfHands"] = int(line.rstrip())
                line = f.readline()
                spot["statistics"]["foldNumberOfHandsCorrect"] = int(line.rstrip())
                line = f.readline()
                spot["handTotalArrAttempt"] = self.readArr(line)
                line = f.readline()
                spot["handTotalArrCorrect"] = self.readArr(line)
                line = f.readline()
                spot["handRaiseArrAttempt"] = self.readArr(line)
                line = f.readline()
                spot["handRaiseArrCorrect"] = self.readArr(line)
                line = f.readline()
                spot["handCallArrAttempt"] = self.readArr(line)
                line = f.readline()
                spot["handCallArrCorrect"] = self.readArr(line)
                line = f.readline()
                spot["handFoldArrAttempt"] = self.readArr(line)
                line = f.readline()
                spot["handFoldArrCorrect"] = self.readArr(line)
                return True, line, spotName, spot
            except:
                return False, None, None, None

    # Mode is an int b/t 1 and 3
    # 1 = raise
    # 2 = call
    # 3 = fold
    def addHandData(self, spot, hand, correct,  mode, addTotals):
        if addTotals == True:
            self.addHandData("Total", hand, correct, mode, False)
        if spot not in self.report["data"].keys():
            self.generateSpot(spot)
        handIdx = self.comboMapInverse[hand]
        self.report["data"][spot]["statistics"]["numberOfHands"] += 1
        self.report["data"][spot]["handTotalArrAttempt"][handIdx[0]][handIdx[1]] += 1
        if mode ==1:
            self.report["data"][spot]["statistics"]["raiseNumberOfHands"] += 1
            self.report["data"][spot]["handRaiseArrAttempt"][handIdx[0]][handIdx[1]] += 1
            if correct:
                self.report["data"][spot]["statistics"]["numberOfHandsCorrect"] += 1
                self.report["data"][spot]["statistics"]["raiseNumberOfHandsCorrect"] += 1
                self.report["data"][spot]["handTotalArrCorrect"][handIdx[0]][handIdx[1]] += 1
                self.report["data"][spot]["handRaiseArrCorrect"][handIdx[0]][handIdx[1]] += 1
        if mode ==2:
            self.report["data"][spot]["statistics"]["callNumberOfHands"] += 1
            self.report["data"][spot]["handCallArrAttempt"][handIdx[0]][handIdx[1]] += 1
            if correct:
                self.report["data"][spot]["statistics"]["numberOfHandsCorrect"] += 1
                self.report["data"][spot]["statistics"]["callNumberOfHandsCorrect"] += 1
                self.report["data"][spot]["handTotalArrCorrect"][handIdx[0]][handIdx[1]] += 1
                self.report["data"][spot]["handCallArrCorrect"][handIdx[0]][handIdx[1]] += 1
        if mode ==3:
            self.report["data"][spot]["statistics"]["foldNumberOfHands"] += 1
            self.report["data"][spot]["handFoldArrAttempt"][handIdx[0]][handIdx[1]] += 1
            if correct:
                self.report["data"][spot]["statistics"]["numberOfHandsCorrect"] += 1
                self.report["data"][spot]["statistics"]["foldNumberOfHandsCorrect"] += 1
                self.report["data"][spot]["handTotalArrCorrect"][handIdx[0]][handIdx[1]] += 1
                self.report["data"][spot]["handFoldArrCorrect"][handIdx[0]][handIdx[1]] += 1

    def isEmpty(self):
        return not bool(self.report)
