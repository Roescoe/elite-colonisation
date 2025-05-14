import os
import sys
import json
import ast
import time
import re
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

populated = False

def setUpLogfile(self, directory):
    folderdir = directory
    ext = ('.log')
    createTime = []
    global logFileListSorted
    selectedTime = self.loadDate.currentIndex()
    olderThanNumDays = 0
    currentTime = time.time()

    match selectedTime:
        case 0:
            olderThanNumDays = currentTime - 3600*24*1
        case 1:
            olderThanNumDays = currentTime - 3600*24*7
        case 2:
            olderThanNumDays = currentTime - 3600*24*30
        case 3:
            olderThanNumDays = currentTime - 3600*24*100
        case 4:
            olderThanNumDays = 0
        case _:
            olderThanNumDays = 0

     
    for path, dirc, files in os.walk(folderdir):
        for name in files:
            if name.endswith(ext):
                if os.path.getctime(os.path.join(path, name)) >= olderThanNumDays:
                    logFileList.append(os.path.join(path, name))
                    createTime.append(os.path.getctime(os.path.join(path, name)))
    logFileListSortedPairs = sorted(zip(createTime,logFileList))
    logFileListSorted = [x for _, x in logFileListSortedPairs]
    logFileListSorted.sort(reverse = True)
    print("files*: ",logFileList)
    print("times*: ",createTime)
    print("sorts*: ",logFileListSorted)
    return logFileListSorted

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        print("setting up window")
        
        self.setWindowTitle("Roescoe's Elite Colonisation App")
        self.setGeometry(100, 100, 1000, 100)
        self.dialogLayout = QGridLayout()
        self.resourceLayout = QGridLayout()


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
        
        loadFolderButton = QPushButton()
        loadFolderButton.setText("Load Folder")
        
        loadDateText = QLabel("Load no older than:")
        self.loadDate = QComboBox()
        self.loadDate.addItem("1 Day")
        self.loadDate.addItem("1 Week")
        self.loadDate.addItem("1 Month")
        self.loadDate.addItem("100 Days")
        self.loadDate.addItem("All")
        self.loadDate.setCurrentIndex(2)

        self.shipLabel = QLabel("Ship:")
        self.shipDropdown = QComboBox()
        # self.shipSelectButton = QPushButton("Select Ship")

        self.projectDropdown = QComboBox()
        self.refreshProjectButton = QPushButton()
        self.refreshProjectButton.setText("Update")
        
        quitButton = QPushButton()
        quitButton.setText("Quit")

        self.dialogLayout.addWidget(folderLoad, 0, 1)
        self.dialogLayout.addWidget(loadDateText,0,2)
        self.dialogLayout.addWidget(self.loadDate,0,3)
        self.dialogLayout.addWidget(loadFolderButton, 0, 4)
        
        
        self.dialogLayout.addWidget(quitButton, 100, 0)
        self.setLayout(self.dialogLayout)
        
        loadFolderButton.clicked.connect(lambda: loadFile(self, lineEdits[0].text()))
        self.refreshProjectButton.clicked.connect(lambda: refreshUniqueEntries(self, ["ColonisationConstructionDepot"], "MarketID"))
        quitButton.clicked.connect(lambda: quitNow())

def loadFile(self, directory):
    print("loading files")
    logFileListSorted = setUpLogfile(self, directory)
    data = findUniqueEntries(["ColonisationConstructionDepot"], "MarketID")

    self.dialogLayout.addWidget(self.shipLabel, 1, 2)
    self.dialogLayout.addWidget(self.shipDropdown, 1, 3)
    # self.dialogLayout.addWidget(self.shipSelectButton, 1, 4)
    ships = []
    loadouts = findShips()
    for ship in loadouts:
        ships.append(str(ship) +": "+ str(loadouts[ship])+"T")
    print("loadouts:", loadouts)
    print("Type:", type(loadouts))
    print("Ships:", ships)
    self.shipDropdown.clear()
    self.shipDropdown.addItems(ships)

    with open("settings.txt", "w") as s:
        s.write("Folder_location: ")
        s.write(directory)
    with open("allColonyLandings.txt", "w") as f:
        f.write("\n".join(map(str, data.values())))

    print("Number of Stations: ",len(data))
    print("values: ",uniqueStations.values())
    self.projectDropdown.clear()
    self.projectDropdown.addItems(uniqueStations.values())
    self.dialogLayout.addWidget(self.projectDropdown, 2, 1)
    self.dialogLayout.addWidget(self.refreshProjectButton, 2, 2)
    self.setLayout(self.dialogLayout)

def populateTable(self):
    global populated
    print("Populating table:")
    startIndex = 3
    projectID = -1
    totalProvidedResources = 0
    totalNeededResources = 0
    currentTonnage = 0

    currentSelectedProjectName = self.projectDropdown.currentText()
    
    projectID = [key for key, val in uniqueStations.items() if val == currentSelectedProjectName]
    print("project ID: ", projectID)
    print("project name: ", self.projectDropdown.currentText())
    
    
    # print("Populated: ",populated)
    if populated:
        while self.resourceLayout.count():
            item = self.resourceLayout.itemAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater() 
            self.resourceLayout.removeItem(item)
    self.resourceLayout.addWidget(QLabel("Trips Left:"), 1, 3)
    
    print(" SUB1: ",self.shipDropdown.currentText().rsplit(" ",1)[1].split("T")[0])
    currentTonnage = int(self.shipDropdown.currentText().rsplit(" ",1)[1].split("T")[0])
    
    self.resourceLayout.addWidget(QLabel("Resource"), startIndex-1, 0)
    self.resourceLayout.addWidget(QLabel("Total Need"), startIndex-1, 1)
    self.resourceLayout.addWidget(QLabel("Current Need"), startIndex-1, 2)
    with open("allColonyLandings.txt", "r") as f:
        for line in f:
            testFileLine = ast.literal_eval(line)
            print("reading line: ",testFileLine)
            if testFileLine["MarketID"] == projectID[0]:
                resources = testFileLine["ResourcesRequired"]
                print("resources: ",resources)
                for i in range(len(resources)):
                    print("from file:", resources[i])
                    print("resource: ", resources[i]["Name_Localised"])
                    print("resource amount: ", resources[i]["RequiredAmount"])
                    print("resource provided: ", resources[i]["ProvidedAmount"])
                    self.resourceLayout.addWidget(QLabel(resources[i]["Name_Localised"]), startIndex, 0)
                    self.resourceLayout.addWidget(QLabel(str(resources[i]["RequiredAmount"])), startIndex, 1)
                    remaining = str(resources[i]["RequiredAmount"]-resources[i]["ProvidedAmount"])
                    remainingLabel = QLabel(remaining)
                    if (remaining == "0"):
                        remainingLabel.setStyleSheet("background-color: green")
                    elif(int(remaining) == resources[i]["RequiredAmount"]):
                        remainingLabel.setStyleSheet("QLabel { color : navy; background-color : yellow; }")
                    else:
                        remainingLabel.setStyleSheet("QLabel { color : navy; background-color : pink; }")
                    self.resourceLayout.addWidget(remainingLabel, startIndex, 2)
                    startIndex += 1
                    totalProvidedResources += resources[i]["ProvidedAmount"]
                    totalNeededResources += resources[i]["RequiredAmount"]
    trips = str(round((totalNeededResources-totalProvidedResources)/currentTonnage,2)) if currentTonnage > 0 else "No Cargo"
    self.resourceLayout.addWidget(QLabel(trips), 1, 4)
    print("total resources: ", startIndex-2)
    self.dialogLayout.addLayout(self.resourceLayout,4,0)
    populated = True

def quitNow():
    sys.exit()

def findUniqueEntries (eventList, uniqueId):
    
    
    for logfile in logFileListSorted:
        with open(logfile, "r", encoding='iso-8859-1') as f:
            for line in f:
                rawLine = json.loads(line)
                if "MarketID" in rawLine and "StationName" in rawLine: 
                    uniqueStations[rawLine["MarketID"]] = rawLine["StationName"]
                if any(event in line for event in eventList):
                    if(rawLine.get(uniqueId) not in uniqueIDs): #it's a new market ID we want
                        firstInstanceInFile[rawLine.get(uniqueId)] = str(logfile)
                        uniqueIDs.append(rawLine.get(uniqueId))
                        data[rawLine.get(uniqueId)] = rawLine
                    #only update if id and filename are still the same as first find
                    if(rawLine.get(uniqueId) in uniqueIDs and firstInstanceInFile[rawLine.get(uniqueId)] == str(logfile)):
                        data[rawLine.get(uniqueId)] = rawLine

    for key in list(uniqueStations.keys()):
        if key not in uniqueIDs:
            del uniqueStations[key]
    print("ids: ", uniqueIDs)
    print("Stations: ", uniqueStations.keys())
    return data

def refreshUniqueEntries (self, eventList, uniqueId):


    logfile = logFileListSorted[0]
    lineCount = 0
    with open(logfile, "r", encoding='iso-8859-1') as f:
        for line in f:
            lineCount += 1
            rawLine = json.loads(line)
            if "MarketID" in rawLine and "StationName" in rawLine: 
                uniqueStations[rawLine["MarketID"]] = rawLine["StationName"]
            if any(event in line for event in eventList):
                if(rawLine.get(uniqueId) not in uniqueIDs): #it's a new market ID we want
                    print("ID is: ",rawLine.get(uniqueId))
                    firstInstanceInFile[rawLine.get(uniqueId)] = str(logfile)
                    uniqueIDs.append(rawLine.get(uniqueId))
                    data[rawLine.get(uniqueId)] = rawLine
                #only update if id and filename are still the same as first find
                if(rawLine.get(uniqueId) in uniqueIDs and firstInstanceInFile[rawLine.get(uniqueId)] == str(logfile)):
                    data[rawLine.get(uniqueId)] = rawLine

    for key in list(uniqueStations.keys()):
        if key not in uniqueIDs:
            del uniqueStations[key]
    with open("allColonyLandings.txt", "w") as f:
        f.write("\n".join(map(str, data.values())))
    print("******Lines in current logfile:*******", lineCount)
    populateTable(self)

def findShips():
    #"event":"Loadout"
    print("Loading Ships")
    
    latestLoadout = {}

    for logfile in logFileListSorted:
        with open(logfile, "r", encoding='iso-8859-1') as f:
            for line in f:
                rawLine = json.loads(line)
                if "ShipIdent" in rawLine and "CargoCapacity" in rawLine: 
                    if rawLine["ShipIdent"] not in latestLoadout:
                        latestLoadout[rawLine["ShipIdent"]] = logfile
                        loadouts[rawLine["ShipIdent"]] = rawLine["CargoCapacity"]
                    if rawLine["ShipIdent"] in latestLoadout and logfile == latestLoadout[rawLine["ShipIdent"]]:
                        loadouts[rawLine["ShipIdent"]] = rawLine["CargoCapacity"]
    return loadouts

if __name__ == '__main__':
    loadouts = {}
    data = {}
    firstInstanceInFile = {} # {marketID:logfile} dictionary
    logFileList = []
    uniqueStations = {}
    uniqueIDs = []
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
