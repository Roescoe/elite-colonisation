import os
import sys
import json
import ast
import time
import re
import copy
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

# This is a tool to print out Elite Dangerous colonization data pulled from the user's logfiles
# Copyright (C) 2025 Roescoe

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
        self.statsLayout = QGridLayout()


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

        self.projectDropdown = QComboBox()
        self.refreshProjectButton = QPushButton("Update")
        self.hideFinished = QCheckBox("Hide Finished Resources")

        quitButton = QPushButton("Quit")
        
        with open("settings.txt", "r") as f:
            settingsFileLines = f.readlines()
            for line in settingsFileLines:
                print("Settings line: ", line)
                if line.startswith("Load_time_selection:"):
                    print("Found time in settings")
                    self.loadDate.setCurrentIndex(int(line.split("Load_time_selection: ",1)[1].strip()))
                if line.startswith("Hide_resources:"):
                    print("Found checkbox in settings \'"+ line.split("Hide_resources: ",1)[1].strip()+"\'")
                    print("Type "+ str(type(int(line.split("Hide_resources: ",1)[1].strip()))))
                    if isinstance(int(line.split("Hide_resources: ",1)[1].strip()), int):
                        hideBoxIsChecked = bool(int(line.split("Hide_resources: ",1)[1].strip()))
                        self.hideFinished.setChecked(hideBoxIsChecked)

        self.dialogLayout.addWidget(folderLoad, 1, 0)
        self.dialogLayout.addWidget(loadDateText,2,0)
        self.dialogLayout.addWidget(self.loadDate,2,1)
        self.dialogLayout.addWidget(loadFolderButton, 1, 1)

        self.dialogLayout.addWidget(quitButton, 100, 1)
        self.setLayout(self.dialogLayout)
        
        loadFolderButton.clicked.connect(lambda: loadFile(self, lineEdits[0].text()))
        self.refreshProjectButton.clicked.connect(lambda: refreshUniqueEntries(self, ["ColonisationConstructionDepot"], "MarketID"))
        
        quitButton.clicked.connect(lambda: quitNow(self, lineEdits[0].text()))

def loadFile(self, directory):
    print("loading files")
    logFileListSorted = setUpLogfile(self, directory)
    data = findUniqueEntries(["ColonisationConstructionDepot"], "MarketID")
    self.shipLabel.setAlignment(Qt.AlignmentFlag.AlignRight)

    # self.hideFinished.setAlignment(Qt.AlignmentFlag.AlignRight)
    # self.hideFinished.setStyleSheet("text-align: right;")
    self.dialogLayout.addWidget(self.shipLabel, 3, 0)
    self.dialogLayout.addWidget(self.shipDropdown, 3, 1)
    self.dialogLayout.addWidget(self.hideFinished,4, 1)
    ships = []
    loadouts = findShips()
    for ship in loadouts:
        ships.append(str(ship) +": "+ str(loadouts[ship])+"T")
    print("loadouts:", loadouts)
    print("Type:", type(loadouts))
    print("Ships:", ships)
    self.shipDropdown.clear()
    self.shipDropdown.addItems(ships)

    # with open("settings.txt", "w") as s:
    #     s.write("Folder_location: ")
    #     s.write(directory)
    with open("allColonyLandings.txt", "w") as f:
        f.write("\n".join(map(str, data.values())))

    print("Number of Stations: ",len(data))
    print("values: ",uniqueStations.values())
    self.projectDropdown.clear()
    self.projectDropdown.addItems(uniqueStations.values())
    self.dialogLayout.addWidget(self.projectDropdown, 3, 0)
    self.dialogLayout.addWidget(self.refreshProjectButton, 3, 1)
    self.setLayout(self.dialogLayout)

def populateTable(self, *args):
    global populated
    print("Populating table:")
    startIndex = 7
    projectID = -1
    totalProvidedResources = 0
    totalNeededResources = 0
    currentTonnage = 0
    resourceTable = []
    sortType = "none"
    HideFinishedResources = False


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
        while self.statsLayout.count():
            item = self.statsLayout.itemAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater() 
            self.statsLayout.removeItem(item)

    currentTonnage = int(self.shipDropdown.currentText().rsplit(" ",1)[1].split("T")[0])


    sortByResName = QPushButton("Sort by Resource")
    sortByResTotal = QPushButton("Sort by Total")
    sortByResNeed = QPushButton("Sort by Need")
    
    
    self.resourceLayout.addWidget(sortByResName,startIndex - 2, 0)
    self.resourceLayout.addWidget(sortByResTotal,startIndex - 2, 1)
    self.resourceLayout.addWidget(sortByResNeed,startIndex - 2, 2)
    
    self.resourceLayout.addWidget(QLabel("Resource"), startIndex - 1, 0)
    self.resourceLayout.addWidget(QLabel("Total Need"), startIndex - 1, 1)
    self.resourceLayout.addWidget(QLabel("Current Need"), startIndex - 1, 2)
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    self.resourceLayout.addWidget(line, startIndex, 0, 1, 20)



    with open("allColonyLandings.txt", "r") as f:
        for line in f:
            testFileLine = ast.literal_eval(line)
            if testFileLine["MarketID"] == projectID[0]:
                resources = testFileLine["ResourcesRequired"]
                print("resources: ",resources)
                for i in range(len(resources)):
                    print("from file:", resources[i])
                    print("resource: ", resources[i]["Name_Localised"])
                    print("resource amount: ", resources[i]["RequiredAmount"])
                    print("resource provided: ", resources[i]["ProvidedAmount"])
                    resourceLabel = resources[i]["Name_Localised"]
                    resourceAmount = str(resources[i]["RequiredAmount"])
                    remainingLabel = str(resources[i]["RequiredAmount"]-resources[i]["ProvidedAmount"])
                     
                    resourceTuple = resourceLabel, resourceAmount, remainingLabel
                    resourceTable.append(resourceTuple)
                    totalProvidedResources += resources[i]["ProvidedAmount"]
                    totalNeededResources += resources[i]["RequiredAmount"]
    trips = str(round((totalNeededResources-totalProvidedResources)/currentTonnage,1)) if currentTonnage > 0 else "No Cargo"
    percentComplete = str(round(totalProvidedResources/totalNeededResources*100,2))+"%"
    percentPerTrip = str(round(currentTonnage/totalNeededResources*100,2))+"%" if currentTonnage > 0 else "No Cargo"
    printTable = copy.deepcopy(resourceTable)

    if len(args) >= 2:
        HideFinishedResources = args[1]   
    if HideFinishedResources:
        self.hideFinished.setChecked(True)
        printTable = [p for p in printTable if "0" not in p]

    if len(args) >= 1:
        sortType = args[0]
    if sortType == "Resource":
        printTable.sort(key = lambda x: x[0])
    if sortType == "Total":    
        printTable.sort(key = lambda y: (int(y[1]),y[0]))
    if sortType == "Need": 
        printTable.sort(key = lambda z: (int(z[2]),z[0]))

    self.statsLayout.addWidget(QLabel("Trips Left:"), 0, 0)
    self.statsLayout.addWidget(QLabel(trips), 0, 1)
    self.statsLayout.addWidget(QLabel("Percent Complete:"), 0, 2)
    self.statsLayout.addWidget(QLabel(percentComplete), 0, 3)
    self.statsLayout.addWidget(QLabel("Percent per Trip:"), 1, 0)
    self.statsLayout.addWidget(QLabel(percentPerTrip), 1, 1)
    self.statsLayout.addWidget(QLabel("Total Materials:"), 1, 2)
    self.statsLayout.addWidget(QLabel(str(totalNeededResources)), 1, 3)
    self.statsLayout.addWidget(QLabel("Still Needed"), 2, 2)
    self.statsLayout.addWidget(QLabel(str(totalNeededResources-totalProvidedResources)), 2, 3)

    for i,(resourceName, resourceTotal, remaining) in enumerate(printTable):
        self.resourceLayout.addWidget(QLabel(resourceName), i + startIndex + 1, 0)
        self.resourceLayout.addWidget(QLabel(resourceTotal), i + startIndex + 1, 1)
        remainingLabel = QLabel(remaining)
        if (remaining == "0"):
            remainingLabel.setStyleSheet("background-color: green")
        elif(int(remaining) == int(resourceTotal)):
            remainingLabel.setStyleSheet("QLabel { color : navy; background-color : yellow; }")
        else:
            remainingLabel.setStyleSheet("QLabel { color : navy; background-color : pink; }")
        self.resourceLayout.addWidget(remainingLabel, i + startIndex + 1, 2)
        
    self.dialogLayout.addLayout(self.statsLayout,5, 0, 1, 3)
    self.dialogLayout.addLayout(self.resourceLayout,6, 0, 1, 3)
    populated = True

    sortByResName.clicked.connect(lambda: populateTable(self, "Resource", self.hideFinished.isChecked()))
    sortByResTotal.clicked.connect(lambda: populateTable(self, "Total", self.hideFinished.isChecked()))
    sortByResNeed.clicked.connect(lambda: populateTable(self,"Need", self.hideFinished.isChecked()))

def quitNow(self, directory):
    with open("settings.txt", "w") as f:
        f.write("Folder_location: ")
        f.write(directory)
        f.write("\nHide_resources: ")
        f.write(str(int(self.hideFinished.isChecked())))
        f.write("\nLoad_time_selection: ")
        f.write(str(self.loadDate.currentIndex()))
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
    populateTable(self, "Resource", self.hideFinished.isChecked())

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
