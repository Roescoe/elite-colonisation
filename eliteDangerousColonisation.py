import os
import sys
import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *


logFileList = []
data = []

def setUpLogfile(directory):
    folderdir = directory
    ext = ('.log')
     
    for path, dirc, files in os.walk(folderdir):
        for name in files:
            if name.endswith(ext):
                logFileList.append(os.path.join(path, name))
    return logFileList.sort()

def setUpWindow():
    print("setting up window")
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("Roescoe's Elite Colonisation App")
    window.setGeometry(100, 100, 1000, 100)
    dialogLayout = QGridLayout()


    lineEdits = []
    for x in range(5):
        lineEdit = QLineEdit()
        lineEdit.setMaxLength(300)
        lineEdits.append(lineEdit)
    dialogLayout.addWidget(QLabel("Logfile folder (usually under Saved Games):"), 0, 0)
    dialogLayout.addWidget(lineEdits[0], 0, 1)
    
    loadFolderButton = QPushButton()
    loadFolderButton.setText("Load Folder")
    formatDropdown = QComboBox()
    dialogLayout.addWidget(loadFolderButton, 0, 3)
    formatDropdown.addItem("Audio - MP3")
    formatDropdown.addItem("Video - MP4")
    dialogLayout.addWidget(formatDropdown)
    quitButton = QPushButton()
    quitButton.setText("Quit")

    dialogLayout.addWidget(quitButton)
    window.setLayout(dialogLayout)
    window.show()
    loadFolderButton.clicked.connect(lambda: loadFile(lineEdits[0].text()))
    quitButton.clicked.connect(lambda: quitNow())
    sys.exit(app.exec())
    

def quitNow():
    sys.exit()

def loadFile(directory):
    print("loading file")
    logFileList = setUpLogfile(directory)
    findUniqueEntries(["ColonisationConstructionDepot"], "MarketID")
    with open("allColonyLandings.txt", "w") as f:
        f.write(str(data))


def findUniqueEntries (eventList, uniqueId):
    uniqueIDs = []
    for logfile in logFileList:
        with open(logfile) as f:
            for line in f:
                if any(event in line for event in eventList):
                    rawLine = json.loads(line)
                    if(rawLine.get(uniqueId) not in uniqueIDs):
                        data.append(rawLine)
                        uniqueIDs.append(rawLine.get(uniqueId))
                        print(rawLine.get(uniqueId))
    return data

# def printEntries (data, eventList, eventAttributeList):
#     if len(eventAttributeList) is not len(eventList):
#         return
#     for e in data:
#         for selectedEvent, item in zip(eventList, eventAttributeList):
#             if e["event"] == selectedEvent:
#                 with open("output3.txt", "a") as f:
#                     f.write("%s: " % selectedEvent)
#                     f.write("\n    ")
#                     for i in item:
#                         f.write(str(e[i]))
#                     f.write("")

setUpWindow()





