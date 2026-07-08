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
        spot["handAllinArrAttempt"] = np.zeros((13, 13), dtype=np.int32)
        spot["handAllinArrCorrect"] = np.zeros((13, 13), dtype=np.int32)
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
        spot["statistics"]["allinNumberOfHands"] = 0
        spot["statistics"]["allinNumberOfHandsCorrect"] = 0
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
                    # All-In data is appended after the fold data so that older
                    # reports (which stop here) remain loadable.
                    f.write(str(spot["statistics"]["allinNumberOfHands"]) +"\n")
                    f.write(str(spot["statistics"]["allinNumberOfHandsCorrect"]) +"\n")
                    self.writeArr(f, spot["handAllinArrAttempt"])
                    self.writeArr(f, spot["handAllinArrCorrect"])
            return True
        except:
            return False

    def writeArr(self, f, arr):
        arr = arr.flatten()
        for i in range(len(arr)-1):
            f.write(str(arr[i]) + ",")
        f.write(str(arr[-1]) + "\n")

    def readArr(self, line):
        arr = np.zeros((169), dtype=np.int32)
        line = line.split(",")
        # int(float(...)) so values written as "17" or "17.0" both load
        for idx in range(168):
            arr[idx] = int(float(line[idx]))
        arr[-1] = int(float(line[-1].rstrip()))
        arr = arr.reshape((13, 13))
        return arr

    def isInt(self, s):
        try:
            int(s)
            return True
        except:
            return False

    def loadReport(self, filename):
        self.clearReport()
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
            self.report["name"] = lines[0].rstrip()
            self.report["data"] = {}
            i = 1
            while i < len(lines):
                if lines[i].strip() == "":
                    i += 1
                    continue
                try:
                    i, spotName, spot = self.loadSpot(lines, i)
                except:
                    # Stop on a malformed/truncated spot, keeping earlier ones
                    break
                self.report["data"][spotName] = spot
            return True
        except:
            return False

    def loadSpot(self, lines, i):
        spotName = lines[i].rstrip(); i += 1
        stats = {}
        stats["numberOfHands"] = int(lines[i].rstrip()); i += 1
        stats["numberOfHandsCorrect"] = int(lines[i].rstrip()); i += 1
        stats["raiseNumberOfHands"] = int(lines[i].rstrip()); i += 1
        stats["raiseNumberOfHandsCorrect"] = int(lines[i].rstrip()); i += 1
        stats["callNumberOfHands"] = int(lines[i].rstrip()); i += 1
        stats["callNumberOfHandsCorrect"] = int(lines[i].rstrip()); i += 1
        stats["foldNumberOfHands"] = int(lines[i].rstrip()); i += 1
        stats["foldNumberOfHandsCorrect"] = int(lines[i].rstrip()); i += 1
        spot = {}
        spot["statistics"] = stats
        spot["handTotalArrAttempt"] = self.readArr(lines[i]); i += 1
        spot["handTotalArrCorrect"] = self.readArr(lines[i]); i += 1
        spot["handRaiseArrAttempt"] = self.readArr(lines[i]); i += 1
        spot["handRaiseArrCorrect"] = self.readArr(lines[i]); i += 1
        spot["handCallArrAttempt"] = self.readArr(lines[i]); i += 1
        spot["handCallArrCorrect"] = self.readArr(lines[i]); i += 1
        spot["handFoldArrAttempt"] = self.readArr(lines[i]); i += 1
        spot["handFoldArrCorrect"] = self.readArr(lines[i]); i += 1
        # All-In block is optional. In new reports the line after the fold data
        # is an integer (allinNumberOfHands); in older reports it is the next
        # spot name (never a bare integer), so we can detect it safely.
        if i < len(lines) and self.isInt(lines[i].rstrip()):
            stats["allinNumberOfHands"] = int(lines[i].rstrip()); i += 1
            stats["allinNumberOfHandsCorrect"] = int(lines[i].rstrip()); i += 1
            spot["handAllinArrAttempt"] = self.readArr(lines[i]); i += 1
            spot["handAllinArrCorrect"] = self.readArr(lines[i]); i += 1
        else:
            stats["allinNumberOfHands"] = 0
            stats["allinNumberOfHandsCorrect"] = 0
            spot["handAllinArrAttempt"] = np.zeros((13, 13), dtype=np.int32)
            spot["handAllinArrCorrect"] = np.zeros((13, 13), dtype=np.int32)
        return i, spotName, spot

    # Mode is an int b/t 1 and 4
    # 1 = raise
    # 2 = call
    # 3 = fold
    # 4 = raise all-in
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
        if mode ==4:
            self.report["data"][spot]["statistics"]["allinNumberOfHands"] += 1
            self.report["data"][spot]["handAllinArrAttempt"][handIdx[0]][handIdx[1]] += 1
            if correct:
                self.report["data"][spot]["statistics"]["numberOfHandsCorrect"] += 1
                self.report["data"][spot]["statistics"]["allinNumberOfHandsCorrect"] += 1
                self.report["data"][spot]["handTotalArrCorrect"][handIdx[0]][handIdx[1]] += 1
                self.report["data"][spot]["handAllinArrCorrect"][handIdx[0]][handIdx[1]] += 1

    def isEmpty(self):
        return not bool(self.report)
