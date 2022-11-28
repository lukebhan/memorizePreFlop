from PyQt5.QtCore import Qt
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class TrainingReports():
    def __init__(self):
        self.generalTab = QWidget()
        self.layout = QVBoxLayout()
        button = QPushButton("TEST")
        button.clicked.connect(self.clicked)
        self.layout.addWidget(QCheckBox("General Option 1"))
        self.layout.addWidget(QCheckBox("General Option 2"))
        self.layout.addWidget(button)
        self.generalTab.setLayout(self.layout)

    def getWindow(self):
        return self.generalTab

    def clicked(self):
        print("CLICKED")


