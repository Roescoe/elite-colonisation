import os
import sys
import json
import ast
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *





def setUpLogfile(directory):
    folderdir = directory
    ext = ('.log')
    createTime = []
    global logFileListSorted

     
    for path, dirc, files in os.walk(folderdir):
        for name in files:
            if name.endswith(ext):
                logFileList.append(os.path.join(path, name))
                createTime.append(os.path.getctime(os.path.join(path, name)))
    logFileListSortedPairs = sorted(zip(createTime,logFileList))
    logFileListSorted = [x for _, x in logFileListSortedPairs]
    
    return logFileListSorted



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
        if os.path.exists("settings.txt"):
            with open("settings.txt", "r") as f:
                testFileLine = f.readline()
                if testFileLine.startswith("Folder_location:"):
                    folderLoad.setText(testFileLine.split("Folder_location: ",1)[1].strip())
                    print("found default folder:", testFileLine.split("Folder_location: ",1)[1].strip())
        self.dialogLayout.addWidget(folderLoad, 0, 1)
        
        loadFolderButton = QPushButton()
        loadFolderButton.setText("Load Folder")
        
        self.dialogLayout.addWidget(loadFolderButton, 0, 2)
        self.selectProjectButton = QPushButton()
        self.projectDropdown = QComboBox()
        
        quitButton = QPushButton()
        quitButton.setText("Quit")

        self.dialogLayout.addWidget(quitButton, 100, 0)
        self.setLayout(self.dialogLayout)
        
        loadFolderButton.clicked.connect(lambda: loadFile(self, lineEdits[0].text()))
        self.selectProjectButton.clicked.connect(lambda: populateTable(self))
        quitButton.clicked.connect(lambda: quitNow())

def loadFile(self, directory):
    print("loading files")
    logFileListSorted = setUpLogfile(directory)
    data = findUniqueEntries(["ColonisationConstructionDepot"], "MarketID")
    with open("settings.txt", "w") as s:
        s.write("Folder_location: ")
        s.write(directory)
    with open("allColonyLandings.txt", "w") as f:
        f.write("\n".join(map(str, data)))

    
    print("values: ",uniqueStations.values())
    self.projectDropdown.addItems(uniqueStations.values())
    self.dialogLayout.addWidget(self.projectDropdown, 1, 1)
    self.selectProjectButton.setText("Select Project")
    self.dialogLayout.addWidget(self.selectProjectButton, 1, 2)
    self.setLayout(self.dialogLayout)

def populateTable(self):
    print("Populating table:")
    startIndex = 5
    projectID = -1

    currentSelectedProjectName = self.projectDropdown.currentText()
    
    projectID = [key for key, val in uniqueStations.items() if val == currentSelectedProjectName]
    print("project ID: ", projectID)
    print("project name: ", self.projectDropdown.currentText())
    self.dialogLayout.addWidget(QLabel("Resource"), 4, 0)
    self.dialogLayout.addWidget(QLabel("Total Need"), 4, 1)
    self.dialogLayout.addWidget(QLabel("Current Need"), 4, 2)
    with open("allColonyLandings.txt", "r") as f:
        for line in f:
            testFileLine = ast.literal_eval(line)
            if testFileLine["MarketID"] == projectID[0]:
                resources = testFileLine["ResourcesRequired"]
                print("resources: ",resources)
                for i in range(len(resources)):
                    print("from file:", resources[i])
                    print("type? ", type(resources))
                    print("resource: ", resources[i]["Name_Localised"])
                    print("resource: ", resources[i]["RequiredAmount"])
                    self.dialogLayout.addWidget(QLabel(resources[i]["Name_Localised"]), startIndex, 0)
                    self.dialogLayout.addWidget(QLabel(str(resources[i]["RequiredAmount"])), startIndex, 1)
                    self.dialogLayout.addWidget(QLabel(str(resources[i]["RequiredAmount"]-resources[i]["ProvidedAmount"])), startIndex, 2)
                    startIndex += 1
    print("total resources: ", startIndex-3)
    self.setLayout(self.dialogLayout)

def quitNow():
    sys.exit()


def findUniqueEntries (eventList, uniqueId):
    data = []
    uniqueIDs = []
    for logfile in logFileListSorted:
        with open(logfile, "r", encoding='iso-8859-1') as f:
            for line in f:
                rawLine = json.loads(line)
                if "MarketID" in rawLine and "StationName" in rawLine: 
                    uniqueStations[rawLine["MarketID"]] = rawLine["StationName"]
                if any(event in line for event in eventList):
                    if(rawLine.get(uniqueId) not in uniqueIDs):
                        data.append(rawLine)
                        uniqueIDs.append(rawLine.get(uniqueId))

    for key in list(uniqueStations.keys()):
        if key not in uniqueIDs:
            del uniqueStations[key]


    print("ids: ", uniqueIDs)
    print("Stations: ", uniqueStations.keys())

    return data

if __name__ == '__main__':
    
    logFileList = []
    uniqueStations = {}
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
# setUpWindow()





