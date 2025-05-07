import os
import sys
import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

folderdir = ''
 
ext = ('.log')
logFileList = []
 
for path, dirc, files in os.walk(folderdir):
    for name in files:
        if name.endswith(ext):
            logFileList.append(os.path.join(path, name))
logFileList.sort()

def setUpWindow():
    print("setting up window")
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("Roescoe's Elite Colonisation App")
    window.setGeometry(100, 100, 1000, 100)
    dialogLayout = QVBoxLayout()
    formLayout = QFormLayout()

    lineEdits = []
    for x in range(5):
        lineEdit = QLineEdit()
        lineEdit.setMaxLength(120)
        lineEdits.append(lineEdit)

    formLayout.addRow("Logfile folder (usually under Saved Games):", lineEdits[0])
    loadFolderButton = QPushButton()
    loadFolderButton.setText("Load Folder")
    formatDropdown = QComboBox()
    formatDropdown.addItem("Audio - MP3")
    formatDropdown.addItem("Video - MP4")
    formLayout.addWidget(formatDropdown)
    quitButton = QPushButton()
    quitButton.setText("Quit")
    dialogLayout.addLayout(formLayout)
    dialogLayout.addWidget(quitButton)
    window.setLayout(dialogLayout)
    window.show()
    loadFileButton.clicked.connect(lambda: quitNow())
    quitButton.clicked.connect(lambda: quitNow())
    sys.exit(app.exec())
    

def quitNow():
    sys.exit()


def findUniqueEntries (eventList, uniqueId):
    data = []
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



def writeColonisationData(events):
    allHits = findUniqueEntries(events, "MarketID")
    with open("allColonyLandings.txt", "w") as f: 
        f.write(str(allHits))

events =["ColonisationConstructionDepot"]


writeColonisationData(events)
setUpWindow()





