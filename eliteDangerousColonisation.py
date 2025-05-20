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
    with open(os.path.join(folderdir, "Market.json"),"r", encoding='iso-8859-1') as f:
        testFileLine = json.load(f)

    for i in testFileLine["Items"]:
        if "Name_Localised" in i and "Category_Localised" in i:
            resourceTypeDict[i["Name_Localised"]] = i["Category_Localised"]
    print("Every resource: ",resourceTypeDict)

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

        self.sortType = "Resource"
        self.needsToReverse = {
            "Type": False,
            "Resource": False,
            "Total": False,
            "Need": False,
            }

        lineEdits = []
        for x in range(5):
            lineEdit = QLineEdit()
            lineEdit.setStyleSheet("color:snow; background-color: #151E3D;")
            lineEdit.setMaxLength(300)
            lineEdits.append(lineEdit)
        fileLoadLabel = QLabel("Logfile folder (usually under Saved Games):")
        fileLoadLabel.setStyleSheet("color:snow; background-color: #151E3D;")
        self.dialogLayout.addWidget(fileLoadLabel)
        folderLoad = lineEdits[0]
        if os.path.exists("settings.txt"):
            with open("settings.txt", "r") as f:
                testFileLine = f.readline()
                if testFileLine.startswith("Folder_location:"):
                    folderLoad.setText(testFileLine.split("Folder_location: ",1)[1].strip())
                    print("found default folder:", testFileLine.split("Folder_location: ",1)[1].strip())
        
        loadFolderButton = QPushButton()
        loadFolderButton.setStyleSheet("color:snow; background-color: #151E3D;")
        loadFolderButton.setText("Load Folder")
        
        loadDateText = QLabel("Load no older than:")
        self.loadDate = QComboBox()
        self.loadDate.addItem("All")
        self.loadDate.setCurrentIndex(2)
        self.shipLabel = QLabel("Ship:")
        self.shipDropdown = QComboBox()
        self.projectDropdown = QComboBox()
        self.refreshProjectButton = QPushButton("Update")
        self.hideFinished = QCheckBox("Hide Finished Resources")
        self.tableSize = QComboBox()

        self.loadDate.addItem("1 Day")
        self.loadDate.addItem("1 Week")
        self.loadDate.addItem("1 Month")
        self.loadDate.addItem("100 Days")
        self.tableSize.addItem("12pt")
        self.tableSize.addItem("16pt")
        self.tableSize.addItem("20pt")
        self.tableSize.addItem("32pt")
        self.tableSize.setCurrentIndex(0)

        quitButton = QPushButton("Quit")

        loadDateText.setStyleSheet("color:snow; background-color: #151E3D;}")
        self.loadDate.setStyleSheet("color:snow; background-color: #151E3D;}")
        self.shipDropdown.setStyleSheet("color:snow; background-color: #151E3D;}")
        self.projectDropdown.setStyleSheet("color:snow; background-color: #151E3D;}")
        self.refreshProjectButton.setStyleSheet("color:snow; background-color: #151E3D;")
        # self.hideFinished.setStyleSheet("color:snow; background-color: #151E3D; QCheckBox::indicator {background-color: snow; };")
        self.tableSize.setStyleSheet("color:snow; background-color: #151E3D;}")
        quitButton.setStyleSheet("color:snow; background-color: #151E3D;")
        
        if os.path.exists("settings.txt"):
            with open("settings.txt", "r") as f:
                settingsFileLines = f.readlines()
                for line in settingsFileLines:
                    print("Settings line: ", line)
                    if line.startswith("Load_time_selection:"):
                        print("Found time in settings")
                        self.loadDate.setCurrentIndex(int(line.split("Load_time_selection: ",1)[1].strip()))
                    if line.startswith("Hide_resources:"):
                        print("Found checkbox in settings \'"+ line.split("Hide_resources: ",1)[1].strip()+"\'")
                        if isinstance(int(line.split("Hide_resources: ",1)[1].strip()), int):
                            hideBoxIsChecked = bool(int(line.split("Hide_resources: ",1)[1].strip()))
                            self.hideFinished.setChecked(hideBoxIsChecked)
                    if line.startswith("Table_size:"):
                        print("Found table size in settings")
                        if isinstance(int(line.split("Table_size: ",1)[1].strip()), int):
                            tableSizeIndex = int(line.split("Table_size: ",1)[1].strip())
                            self.tableSize.setCurrentIndex(tableSizeIndex)

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

    self.dialogLayout.addWidget(self.shipLabel, 4, 0)
    self.dialogLayout.addWidget(self.shipDropdown, 4, 1)
    self.dialogLayout.addWidget(self.hideFinished,5, 1)
    self.dialogLayout.addWidget(QLabel("Table Size:", alignment=Qt.AlignmentFlag.AlignRight), 6, 0)
    self.dialogLayout.addWidget(self.tableSize, 6, 1)
    ships = []
    loadouts = findShips()
    for ship in loadouts:
        ships.append(str(ship) +": "+ str(loadouts[ship])+"T")
    print("loadouts:", loadouts)
    print("Type:", type(loadouts))
    print("Ships:", ships)
    self.shipDropdown.clear()
    self.shipDropdown.addItems(ships)

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
    totalProvidedResources = -1
    totalNeededResources = -1
    currentTonnage = -1
    resourceTable = []
    newResourceTable = []
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

    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    self.resourceLayout.addWidget(line, startIndex, 0, 1, 20)

    with open("allColonyLandings.txt", "r") as f:
        for line in f:
            testFileLine = ast.literal_eval(line)
            if projectID and testFileLine["MarketID"] == projectID[0]:
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
    percentComplete = str(round(totalProvidedResources/totalNeededResources*100,2))+"%"
    if currentTonnage <= 0:
        percentPerTrip = "No Cargo"
        trips = "No Cargo"
    else:
        trips = str(round((totalNeededResources-totalProvidedResources)/currentTonnage,1))
        percentPerTrip = round(currentTonnage/totalNeededResources*100,2)
        if trips <= str(0):
            trips = "Complete!"
        if percentPerTrip <= 0:
            percentPerTrip = "Complete!"
        else:
            percentPerTrip = str(percentPerTrip)+"%"
    if totalNeededResources-totalProvidedResources > 0:
        stillNeeded = totalNeededResources-totalProvidedResources
        stillNeeded = str(f"{stillNeeded:,}")
    else:
        stillNeeded = "Complete!"

    for t in resourceTable:
        tripsPerResource = str(round(int(t[2])/currentTonnage, 1)) if currentTonnage > 0 else "No Cargo"
        resourceType = resourceTypeDict[t[0]]
        newResourceTable.append((resourceType,) + t + (tripsPerResource,))
    if totalNeededResources > 0:
        totalNeededResources =str(f"{int(totalNeededResources):,}")
    else:
        totalNeededResources = "Complete!"

    printTable = copy.deepcopy(newResourceTable)

    for i in args:
        print("Arrrrrgggs: " +str(i))
    if len(args) >= 2:
        HideFinishedResources = args[1]
    if len(args) >= 3:
        self.tableSize.setCurrentIndex(args[2])
    match self.tableSize.currentIndex():
        case 0:
            fontSize = 12
        case 1:
            fontSize = 16
        case 2:
            fontSize = 20
        case 3:
            fontSize = 32
    if HideFinishedResources:
        self.hideFinished.setChecked(True)
        printTable = [p for p in printTable if "0" not in p]

    if len(args) >= 1:
        self.sortType = args[0]
    if self.sortType == "Type":
        printTable.sort(key = lambda x: x[0])
    elif self.sortType == "Resource":
        printTable.sort(key = lambda x: (x[1].lower(),x[1]))
    elif self.sortType == "Total":    
        printTable.sort(key = lambda y: (int(y[2])))
    elif self.sortType == "Need": 
        printTable.sort(key = lambda z: (int(z[3])))
    if self.needsToReverse[self.sortType]:
        printTable.reverse()
        self.needsToReverse[self.sortType] = False
    else:
        self.needsToReverse[self.sortType] = True

    tripsLeftLabel = QLabel("Trips Left:")
    tripsLabel = QLabel(trips)
    percentCompleteLabel = QLabel("Percent Complete:")
    percentCompleteValLabel = QLabel(percentComplete)
    percentPerTripLabel = QLabel("Percent per Trip:")
    percentPerTripValLabel = QLabel(percentPerTrip)
    totalMaterialsLabel = QLabel("Total Materials:")
    totalNeededResourcesCommas = QLabel(totalNeededResources)
    stillNeededLabel = QLabel("Still Needed:")
    stillNeededValLabel = QLabel(stillNeeded)

    tripsLeftLabel.setStyleSheet("color:snow; background-color: #151E3D;}")
    tripsLabel.setStyleSheet("color:snow; background-color: #151E3D;}")
    percentCompleteLabel.setStyleSheet("color:snow; background-color: #151E3D;}")
    percentCompleteValLabel.setStyleSheet("color:snow; background-color: #151E3D;}")
    percentPerTripLabel.setStyleSheet("color:snow; background-color: #151E3D;}")
    percentPerTripValLabel.setStyleSheet("color:snow; background-color: #151E3D;}")
    totalMaterialsLabel.setStyleSheet("color:snow; background-color: #151E3D;}")
    totalNeededResourcesCommas.setStyleSheet("color:snow; background-color: #151E3D;}")
    stillNeededLabel.setStyleSheet("color:snow; background-color: #151E3D;}")
    stillNeededValLabel.setStyleSheet("color:snow; background-color: #151E3D;}")

    tripsLeftLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
    percentCompleteLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
    percentPerTripLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
    totalMaterialsLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
    stillNeededLabel.setAlignment(Qt.AlignmentFlag.AlignRight)

    self.statsLayout.addWidget(tripsLeftLabel, 1, 0)
    self.statsLayout.addWidget(tripsLabel, 1, 1)
    self.statsLayout.addWidget(percentCompleteLabel, 1, 2)
    self.statsLayout.addWidget(percentCompleteValLabel, 1, 3)
    self.statsLayout.addWidget(percentPerTripLabel, 2, 0)
    self.statsLayout.addWidget(percentPerTripValLabel, 2, 1)
    self.statsLayout.addWidget(totalMaterialsLabel, 2, 2)
    self.statsLayout.addWidget(totalNeededResourcesCommas, 2, 3)
    self.statsLayout.addWidget(stillNeededLabel, 3, 2)
    self.statsLayout.addWidget(stillNeededValLabel, 3, 3)

    sortByResType = QPushButton("Category")
    sortByResName = QPushButton("Resource")
    sortByResTotal = QPushButton("Total Need")
    sortByResNeed = QPushButton("Current Need")
    tripsRemaining = QLabel("Trips Remaining")

    sortByResType.setStyleSheet("font-size: "+ str(fontSize) +"px; background-color: #151E3D; color: snow;")
    sortByResName.setStyleSheet("font-size: "+ str(fontSize) +"px; background-color: #151E3D; color: snow;")
    sortByResTotal.setStyleSheet("font-size: "+ str(fontSize) +"px; background-color: #151E3D; color: snow;")
    sortByResNeed.setStyleSheet("font-size: "+ str(fontSize) +"px; background-color: #151E3D; color: snow;")
    tripsRemaining.setStyleSheet("font-size: "+ str(fontSize) +"px; color: snow;")

    self.resourceLayout.addWidget(sortByResType,startIndex - 2, 0)
    self.resourceLayout.addWidget(sortByResName,startIndex - 2, 1)
    self.resourceLayout.addWidget(sortByResTotal,startIndex - 2, 2)
    self.resourceLayout.addWidget(sortByResNeed,startIndex - 2, 3)
    self.resourceLayout.addWidget(tripsRemaining, startIndex - 2, 4)

    for i,(resourceType, resourceName, resourceTotal, remaining, tripsPerResource) in enumerate(printTable):
        resourceTypeLabel = QLabel(resourceType)
        resourceTypeLabel.setStyleSheet("font-size: "+ str(fontSize) +"px; color: snow;")
        self.resourceLayout.addWidget(resourceTypeLabel, i + startIndex + 1, 0)
        remainingLabel = QLabel()
        if (remaining == "0"):
            remainingLabel.setStyleSheet("color: snow; background-color: green; font-size: "+ str(fontSize) +"px;")
        elif(int(remaining) == int(resourceTotal)):
            remainingLabel.setStyleSheet("color: snow; background-color: #c32148; font-size: "+ str(fontSize) +"px;")
        else:
            remainingLabel.setStyleSheet("color: snow; background-color: #281E5D; font-size: "+ str(fontSize) +"px;")
        resourceNameLabel = QLabel(resourceName)
        resourceNameLabel.setStyleSheet("font-size: "+ str(fontSize) +"px; color: snow;")
        self.resourceLayout.addWidget(resourceNameLabel, i + startIndex + 1, 1)
        resourceTotal = f"{int(resourceTotal):,}"
        resourceTotalLabel = QLabel(resourceTotal)
        resourceTotalLabel.setStyleSheet("font-size: "+ str(fontSize) +"px; color: snow;")
        resourceTotalLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.resourceLayout.addWidget(resourceTotalLabel, i + startIndex + 1, 2)
        if remaining == "0":
            remainingLabel.setText("None")
            remainingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            remainingLabel.setText(f"{int(remaining):,}")
            remainingLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.resourceLayout.addWidget(remainingLabel, i + startIndex + 1, 3)
        tripsPerResourceLabel = QLabel(tripsPerResource)
        tripsPerResourceLabel.setStyleSheet("font-size: "+ str(fontSize) +"px; color: snow;")
        tripsPerResourceLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.resourceLayout.addWidget(tripsPerResourceLabel, i + startIndex + 1, 4)
        
    self.dialogLayout.addLayout(self.statsLayout,7, 0, 1, 3)
    self.dialogLayout.addLayout(self.resourceLayout,8, 0, 1, 3)
    populated = True

    sortByResType.clicked.connect(lambda: populateTable(self, "Type", self.hideFinished.isChecked(), self.tableSize.currentIndex()))
    sortByResName.clicked.connect(lambda: populateTable(self, "Resource", self.hideFinished.isChecked(),self.tableSize.currentIndex()))
    sortByResTotal.clicked.connect(lambda: populateTable(self, "Total", self.hideFinished.isChecked(), self.tableSize.currentIndex()))
    sortByResNeed.clicked.connect(lambda: populateTable(self,"Need", self.hideFinished.isChecked(), self.tableSize.currentIndex()))

def quitNow(self, directory):
    with open("settings.txt", "w") as f:
        f.write("Folder_location: ")
        f.write(directory)
        f.write("\nHide_resources: ")
        f.write(str(int(self.hideFinished.isChecked())))
        f.write("\nLoad_time_selection: ")
        f.write(str(self.loadDate.currentIndex()))
        f.write("\nTable_size: ")
        f.write(str(self.tableSize.currentIndex()))
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
    self.needsToReverse[self.sortType] = not self.needsToReverse[self.sortType]
    populateTable(self, self.sortType, self.hideFinished.isChecked(), self.tableSize.currentIndex())

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
    resourceTypeDict = {}
    loadouts = {}
    data = {}
    firstInstanceInFile = {} # {marketID:logfile} dictionary
    logFileList = []
    uniqueStations = {}
    uniqueIDs = []
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setStyleSheet("background-color: black;")
    window.show()
    sys.exit(app.exec())
