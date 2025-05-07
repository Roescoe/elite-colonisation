import os
import sys
import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *


logFileList = []

uniqueStations = {}


def setUpLogfile(directory):
    folderdir = directory
    ext = ('.log')
     
    for path, dirc, files in os.walk(folderdir):
        for name in files:
            if name.endswith(ext):
                logFileList.append(os.path.join(path, name))
    return logFileList.sort()


class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        print("setting up window")
        
        self.setWindowTitle("Roescoe's Elite Colonisation App")
        self.setGeometry(100, 100, 1000, 100)
        self.dialogLayout = QGridLayout()


        lineEdits = []
        for x in range(5):
            lineEdit = QLineEdit()
            lineEdit.setMaxLength(300)
            lineEdits.append(lineEdit)
        self.dialogLayout.addWidget(QLabel("Logfile folder (usually under Saved Games):"))
        folderLoad = lineEdits[0]
        with open("allColonyLandings.txt", "r") as f:
            testFileLine = f.readline()
            if testFileLine.startswith("Folder_location:"):
                folderLoad.setText(testFileLine.split("Folder_location: ",1)[1].strip())
                print("found default folder:", testFileLine.split("Folder_location: ",1)[1].strip())
        self.dialogLayout.addWidget(folderLoad, 0, 1)
        
        loadFolderButton = QPushButton()
        loadFolderButton.setText("Load Folder")
        
        self.dialogLayout.addWidget(loadFolderButton, 0, 2)

        
        quitButton = QPushButton()
        quitButton.setText("Quit")

        self.dialogLayout.addWidget(quitButton, 2, 0)
        self.setLayout(self.dialogLayout)
        
        loadFolderButton.clicked.connect(lambda: loadFile(self, lineEdits[0].text()))
        quitButton.clicked.connect(lambda: quitNow())

def loadFile(self, directory):
    print("loading file")
    logFileList = setUpLogfile(directory)
    data = findUniqueEntries(["ColonisationConstructionDepot"], "MarketID")
    with open("allColonyLandings.txt", "w") as f:
        f.write("Folder_location: ")
        f.write(directory)
        f.write("\n")
        f.write(str(data))
        f.write("\n")
        f.write(str(uniqueStations))
        f.write("\n")
    formatDropdown = QComboBox()
    print("values: ",uniqueStations.values())
    formatDropdown.addItems(uniqueStations.values())
    self.dialogLayout.addWidget(formatDropdown, 1, 1)
    SelectProjectButton = QPushButton()
    SelectProjectButton.setText("Select Project")
    self.dialogLayout.addWidget(SelectProjectButton, 1, 2)
    self.setLayout(self.dialogLayout)

def quitNow():
    sys.exit()


def findUniqueEntries (eventList, uniqueId):
    data = []
    uniqueIDs = []
    for logfile in logFileList:
        with open(logfile) as f:
            for line in f:
                rawLine = json.loads(line)
                if "MarketID" in rawLine and "StationName" in rawLine: 
                    uniqueStations[rawLine["MarketID"]] = rawLine["StationName"]
                if any(event in line for event in eventList):
                    if(rawLine.get(uniqueId) not in uniqueIDs):
                        data.append(rawLine)
                        uniqueIDs.append(rawLine.get(uniqueId))
                        print(rawLine.get(uniqueId))

    for key in list(uniqueStations.keys()):
        if key not in uniqueIDs:
            del uniqueStations[key]


    print("ids: ", uniqueIDs)
    print("Stations: ", uniqueStations.keys())

    return data

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
# setUpWindow()





