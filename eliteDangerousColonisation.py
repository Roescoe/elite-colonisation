import os
import sys
import json
import ast
import time
import copy
import pickle
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

def setUpLogfile(self):
    folderdir = self.folderLoad.text()
    ext = ('.log')
    createTime = []
    selectedTime = self.loadDate.currentIndex()
    olderThanNumDays = 0
    currentTime = time.time()
    logFileList = []

    match selectedTime:
        case 0:
            olderThanNumDays = 0
        case 1:
            olderThanNumDays = currentTime - 3600*24*1
        case 2:
            olderThanNumDays = currentTime - 3600*24*7
        case 3:
            olderThanNumDays = currentTime - 3600*24*30
        case 4:
            olderThanNumDays = currentTime - 3600*24*100
        case _:
            olderThanNumDays = 0

     
    for path, dirc, files in os.walk(folderdir):
        for name in files:
            if name.endswith(ext):
                if os.path.getctime(os.path.join(path, name)) >= olderThanNumDays:
                    logFileList.append(os.path.join(path, name))
                    createTime.append(os.path.getctime(os.path.join(path, name)))
    logFileListSortedPairs = sorted(zip(createTime,logFileList))
    self.logFileListSorted = [x for _, x in logFileListSortedPairs]
    self.logFileListSorted.sort(reverse = True)
    print("files*: ",logFileList)
    print("times*: ",createTime)
    print("sorts*: ",self.logFileListSorted)
    with open("Market.json", "r", encoding='iso-8859-1') as f:
        testFileLine = json.load(f)

    for i in testFileLine["Items"]:
        if "Name_Localised" in i and "Category_Localised" in i:
            self.resourceTypeDict[i["Name_Localised"]] = i["Category_Localised"]
        
    print("Every resource: ",self.resourceTypeDict)

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        print("setting up window")

        self.setWindowTitle("CMDR Roescoe's Elite Colonisation App")
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
        self.logFileListSorted = []
        self.uniqueIDs = []
        self.firstInstanceInFile = {}# {marketID:logfile} dictionary
        self.uniqueStations = {}
        self.data = {}
        self.resourceTypeDict = {}
        self.loadouts = {}
        self.notesBoxes = {}
        self.notesLabels = {}
        self.projectID = -1

        fileLoadLabel = QLabel("Logfile folder (usually under Saved Games):")
        fileLoadLabel.setStyleSheet("color:snow; background-color: #151E3D;")
        self.folderLoad = QLineEdit()
        self.folderLoad.setMaxLength(300)
        self.folderLoad.setStyleSheet("color:snow; background-color: #151E3D;")
        self.dialogLayout.addWidget(fileLoadLabel)
        if os.path.exists("settings.txt"):
            with open("settings.txt", "r") as f:
                testFileLine = f.readline()
                if testFileLine.startswith("Folder_location:"):
                    self.folderLoad.setText(testFileLine.split("Folder_location: ",1)[1].strip())
                    print("found default folder:", testFileLine.split("Folder_location: ",1)[1].strip())
        
        self.loadFolderButton = QPushButton()
        self.loadFolderButton.setStyleSheet("color:snow; background-color: #151E3D;")
        self.loadFolderButton.setText("Load Folder")
        
        loadDateText = QLabel("Load no older than:")
        self.loadDate = QComboBox()
        self.loadDate.setCurrentIndex(2)
        self.projectDropdown = QComboBox()
        self.refreshProjectButton = QPushButton("Update")
        self.shipLabel = QLabel("Ship:")
        self.shipDropdown = QComboBox()
        self.latestLogFile = QLabel()
        self.hideFinished = QCheckBox("Hide Finished Resources")
        self.hideNotes = QCheckBox("Hide Notes")
        self.tableSize = QComboBox()

        self.loadDate.addItem("All")
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

        loadDateText.setStyleSheet("color:snow;}")
        loadDateText.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.latestLogFile.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loadDate.setStyleSheet("color:snow; background-color: #151E3D;}")
        self.projectDropdown.setStyleSheet("color:snow; background-color: #151E3D;}")
        self.refreshProjectButton.setStyleSheet("font-size: 17px;color:snow; background-color: #7c0a02;")
        self.shipDropdown.setStyleSheet("color:snow; background-color: #151E3D;}")
        self.latestLogFile.setStyleSheet("color:snow;}")
        self.hideFinished.setStyleSheet("color:snow; background-color: #151E3D; QCheckBox::indicator {background-color: snow; };")
        self.hideNotes.setStyleSheet("color:snow; background-color: #151E3D; QCheckBox::indicator {background-color: snow; };")
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
                    if line.startswith("Hide_notes:"):
                        print("Found checkbox in settings \'"+ line.split("Hide_notes: ",1)[1].strip()+"\'")
                        if isinstance(int(line.split("Hide_notes: ",1)[1].strip()), int):
                            hideBoxIsChecked = bool(int(line.split("Hide_notes: ",1)[1].strip()))
                            self.hideNotes.setChecked(hideBoxIsChecked)
                    if line.startswith("Table_size:"):
                        print("Found table size in settings")
                        if isinstance(int(line.split("Table_size: ",1)[1].strip()), int):
                            tableSizeIndex = int(line.split("Table_size: ",1)[1].strip())
                            self.tableSize.setCurrentIndex(tableSizeIndex)

        self.dialogLayout.addWidget(self.folderLoad, 1, 0)
        self.dialogLayout.addWidget(loadDateText,2,0)
        self.dialogLayout.addWidget(self.loadDate,2,1)
        self.dialogLayout.addWidget(self.loadFolderButton, 1, 1)

        self.dialogLayout.addWidget(quitButton, 100, 1)
        self.setLayout(self.dialogLayout)
        
        self.loadFolderButton.clicked.connect(lambda: loadFile(self))
        self.refreshProjectButton.clicked.connect(lambda: refreshUniqueEntries(self, "ColonisationConstructionDepot", "MarketID"))
        
        quitButton.clicked.connect(lambda: quitNow(self))

def loadFile(self):
    #rebuild dicts
    self.uniqueStations.clear() 
    self.data.clear()
    self.uniqueIDs.clear()
    print("loading files")
    print("Logfiles?", self.logFileListSorted)
    setUpLogfile(self)
    print("Logfiles SHOULD APPEAR HERE:", self.logFileListSorted)
    findUniqueEntries(self, "ColonisationConstructionDepot", "MarketID")
    self.shipLabel.setAlignment(Qt.AlignmentFlag.AlignRight)

    self.dialogLayout.addWidget(self.shipLabel, 4, 0)
    self.dialogLayout.addWidget(self.shipDropdown, 4, 1)
    self.dialogLayout.addWidget(self.latestLogFile, 5, 0)
    self.dialogLayout.addWidget(self.hideFinished,5, 1)
    self.dialogLayout.addWidget(self.hideNotes,7, 1)
    self.dialogLayout.addWidget(QLabel("Table Size:", alignment=Qt.AlignmentFlag.AlignRight), 6, 0)
    self.dialogLayout.addWidget(self.tableSize, 6, 1)
    ships = []
    findShips(self)
    for shipCargo in self.loadouts:
        ships.append(str(self.loadouts[shipCargo][1]) +": "+ str(shipCargo)+"T" + " (" + str(self.loadouts[shipCargo][0]).capitalize()+ ")")
    print("loadouts:", self.loadouts)
    print("Type:", type(self.loadouts))
    print("Ships:", ships)
    self.shipDropdown.clear()
    self.shipDropdown.addItems(ships)

    with open("allColonyLandings.txt", "w") as f:
        f.write("\n".join(map(str, self.data.values())))

    print("Number of Stations: ",len(self.data))
    print("values: ",self.uniqueStations.values())
    self.projectDropdown.clear()
    stationDropStrings = []
    for key in self.uniqueStations:
        stationDropStrings.append(str(self.uniqueStations[key]) + " (" + str(key)+ ")")
    self.projectDropdown.addItems(stationDropStrings)
    self.dialogLayout.addWidget(self.projectDropdown, 3, 0)
    self.dialogLayout.addWidget(self.refreshProjectButton, 3, 1)
    self.setLayout(self.dialogLayout)

def populateTable(self, *args):
    global populated
    print("Populating table:")
    startIndex = 7
    totalProvidedResources = -1
    totalNeededResources = -1
    currentTonnage = -1
    resourceTable = []
    newResourceTable = []
    HideFinishedResources = False


    if self.projectDropdown.currentText():
        self.projectID = int(self.projectDropdown.currentText().split("(",1)[1].split(")",1)[0])

    print("project ID: ", self.projectID)
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

    currentTonnage = int(self.shipDropdown.currentText().split(" ",3)[1].split("T",1)[0])

    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    self.resourceLayout.addWidget(line, startIndex, 0, 1, 20)

    with open("allColonyLandings.txt", "r") as f:
        for line in f:
            testFileLine = ast.literal_eval(line)
            if self.projectID and testFileLine["MarketID"] == self.projectID:
                resources = testFileLine["ResourcesRequired"]
                # print("resources: ",resources)
                for i in range(len(resources)):
                    resourceLabel = resources[i]["Name_Localised"]
                    resourceAmount = str(resources[i]["RequiredAmount"])
                    remainingLabel = str(resources[i]["RequiredAmount"]-resources[i]["ProvidedAmount"]) 

                    resourceTuple = resourceLabel, resourceAmount, remainingLabel
                    resourceTable.append(resourceTuple)
                    totalProvidedResources += resources[i]["ProvidedAmount"]
                    totalNeededResources += resources[i]["RequiredAmount"]
    if totalProvidedResources == -1: #didn't find any resources provided
        totalProvidedResources = 0

    # Manage stats
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
        if t[0] in self.resourceTypeDict:
            resourceType = self.resourceTypeDict[t[0]]
        else:
            resourceType = "UNKNOWN"
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

    self.notesLabels.clear()
    print("The resource table now: ", printTable)

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
    notesBoxesLabel = QLabel("Notes (press Update to save)")

    sortByResType.setStyleSheet("font-size: "+ str(fontSize) +"px; background-color: #151E3D; color: snow;")
    sortByResName.setStyleSheet("font-size: "+ str(fontSize) +"px; background-color: #151E3D; color: snow;")
    sortByResTotal.setStyleSheet("font-size: "+ str(fontSize) +"px; background-color: #151E3D; color: snow;")
    sortByResNeed.setStyleSheet("font-size: "+ str(fontSize) +"px; background-color: #151E3D; color: snow;")
    tripsRemaining.setStyleSheet("font-size: "+ str(fontSize) +"px; color: snow;")
    notesBoxesLabel.setStyleSheet("font-size: "+ str(fontSize) +"px; color: snow;")
    notesBoxesLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

    self.resourceLayout.addWidget(sortByResType,startIndex - 2, 0)
    self.resourceLayout.addWidget(sortByResName,startIndex - 2, 1)
    self.resourceLayout.addWidget(sortByResTotal,startIndex - 2, 2)
    self.resourceLayout.addWidget(sortByResNeed,startIndex - 2, 3)
    self.resourceLayout.addWidget(tripsRemaining, startIndex - 2, 4)
    if not self.hideNotes.isChecked():
        self.resourceLayout.addWidget(notesBoxesLabel, startIndex - 2, 5)

    for i,(resourceType, resourceName, resourceTotal, remaining, tripsPerResource) in enumerate(printTable):
        resourceTypeLabel = QLabel(resourceType)
        resourceTypeLabel.setStyleSheet("font-size: "+ str(fontSize) +"px; color: snow;")
        resourceTypeLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.resourceLayout.addWidget(resourceTypeLabel, i + startIndex + 1, 0)
        remainingLabel = QLabel()
        remainingLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        if (remaining == "0"):
            remainingLabel.setStyleSheet("color: snow; background-color: green; font-size: "+ str(fontSize) +"px;")
        elif(int(remaining) == int(resourceTotal)):
            remainingLabel.setStyleSheet("color: snow; background-color: #c32148; font-size: "+ str(fontSize) +"px;")
        else:
            remainingLabel.setStyleSheet("color: snow; background-color: #281E5D; font-size: "+ str(fontSize) +"px;")
        resourceNameLabel = QLabel(resourceName)
        resourceNameLabel.setStyleSheet("font-size: "+ str(fontSize) +"px; color: snow;")
        resourceNameLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.resourceLayout.addWidget(resourceNameLabel, i + startIndex + 1, 1)
        resourceTotal = f"{int(resourceTotal):,}"
        resourceTotalLabel = QLabel(resourceTotal)
        resourceTotalLabel.setStyleSheet("font-size: "+ str(fontSize) +"px; color: snow;")
        resourceTotalLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        resourceTotalLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
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

        print("Boooxes: ", self.notesBoxes)
        if not self.hideNotes.isChecked():
            if self.notesBoxes and self.projectID in self.notesBoxes:
                print("loading previous notes: ", self.notesBoxes)
                if resourceName in self.notesBoxes[self.projectID]:
                    print("found resource: ",resourceName)
                    self.notesLabels[resourceName] = QLineEdit(self.notesBoxes[self.projectID][resourceName])
                else:
                    self.notesLabels[resourceName] = QLineEdit()
            else:
                print("adding resource: ",resourceName)
                self.notesLabels[resourceName] = QLineEdit()
            self.notesLabels[resourceName].setStyleSheet("color: snow; background-color: #281E5D; font-size: "+ str(fontSize) +"px;")
            self.resourceLayout.addWidget(self.notesLabels[resourceName], i + startIndex + 1, 5)
        
    self.dialogLayout.addLayout(self.statsLayout,8, 0, 1, 3)
    self.dialogLayout.addLayout(self.resourceLayout,9, 0, 1, 3)

    if self.logFileListSorted:
        lastUpdateTime = time.strftime("%H:%M:%S", time.localtime())
        self.latestLogFile.setText("Latest logfile: "+self.logFileListSorted[0].split("Journal.",1)[1].split(".log",1)[0] + ", Last update: " + lastUpdateTime)
    else:
        self.latestLogFile.setText("No logfiles in path. Either change directory or date range.")

    populated = True

    sortByResType.clicked.connect(lambda: populateTable(self, "Type", self.hideFinished.isChecked(), self.tableSize.currentIndex()))
    sortByResName.clicked.connect(lambda: populateTable(self, "Resource", self.hideFinished.isChecked(),self.tableSize.currentIndex()))
    sortByResTotal.clicked.connect(lambda: populateTable(self, "Total", self.hideFinished.isChecked(), self.tableSize.currentIndex()))
    sortByResNeed.clicked.connect(lambda: populateTable(self,"Need", self.hideFinished.isChecked(), self.tableSize.currentIndex()))

def quitNow(self):
    with open("settings.txt", "w") as f:
        f.write("Folder_location: ")
        f.write(self.folderLoad.text())
        f.write("\nHide_resources: ")
        f.write(str(int(self.hideFinished.isChecked())))
        f.write("\nHide_notes: ")
        f.write(str(int(self.hideNotes.isChecked())))
        f.write("\nLoad_time_selection: ")
        f.write(str(self.loadDate.currentIndex()))
        f.write("\nTable_size: ")
        f.write(str(self.tableSize.currentIndex()))
    sys.exit()

def findUniqueEntries (self, event, uniqueId):
    print("Loading...")
    self.firstInstanceInFile.clear() # {marketID:logfile} dictionary
    for logfile in self.logFileListSorted:
        with open(logfile, "r", encoding='iso-8859-1') as f:
            for line in f:
                rawLine = json.loads(line)
                if "MarketID" in rawLine and "StationName" in rawLine and not rawLine["StationName"].startswith("$EXT_PANEL_"):
                    self.uniqueStations[rawLine["MarketID"]] = rawLine["StationName"]
                    print("found station: ", rawLine["StationName"])
                elif "StationName" in rawLine and rawLine["StationName"].startswith("$EXT_PANEL_") and "StarSystem" in rawLine:
                    print("Found: "+rawLine["StarSystem"] + " and "+ rawLine["StationName"].split("$EXT_PANEL_",1)[1]+ " in "+logfile.split("Journal.",1)[1])
                    self.uniqueStations[rawLine["MarketID"]] = rawLine["StarSystem"] + ": " + rawLine["StationName"].split("$EXT_PANEL_",1)[1]
                if event in line:
                    if(rawLine.get(uniqueId) not in self.uniqueIDs): #it's a new market ID we want
                        self.firstInstanceInFile[rawLine.get(uniqueId)] = str(logfile)
                        print("Load with Logfile: "+ str(logfile))
                        self.uniqueIDs.append(rawLine.get(uniqueId))
                        self.data[rawLine.get(uniqueId)] = rawLine
                    #only update if id and filename are still the same as first find
                    if(rawLine.get(uniqueId) in self.uniqueIDs):
                        if(rawLine.get(uniqueId) in self.firstInstanceInFile):
                            # print("Logfile associated with: "+ str(logfile) + "File: "+ str(firstInstanceInFile[rawLine.get(uniqueId)]))
                            if(self.firstInstanceInFile[rawLine.get(uniqueId)] == str(logfile)):
                                self.data[rawLine.get(uniqueId)] = rawLine

    if os.path.exists("resourceNotes.txt") and os.path.getsize("resourceNotes.txt") > 0:
        with open("resourceNotes.txt", "rb") as f:
            notesFromFile = pickle.load(f)
            print("The notes: ", notesFromFile)
        for marketID in notesFromFile:
            print("First open note: ",marketID)
            for note in notesFromFile[marketID]:
                print("Found note " + note +" in pickle file")
                self.notesBoxes[marketID] = notesFromFile[marketID]
                self.notesBoxes[marketID][note] = notesFromFile[marketID][note]

    for key in list(self.uniqueStations.keys()):
        if key not in self.uniqueIDs:
            del self.uniqueStations[key]
    print("ids: ", self.uniqueIDs)
    print("Stations: ", self.uniqueStations.keys())

def refreshUniqueEntries (self, event, uniqueId):
    notesFromFile = {}

    if self.logFileListSorted:
        logfile = self.logFileListSorted[0]
        print("**Updating from: ", logfile.split("Journal.",1)[1])
        lineCount = 0
        with open(logfile, "r", encoding='iso-8859-1') as f:
            for line in f:
                lineCount += 1
                rawLine = json.loads(line)
                if "MarketID" in rawLine and "StationName" in rawLine and not rawLine["StationName"].startswith("$EXT_PANEL_"):
                    self.uniqueStations[rawLine["MarketID"]] = rawLine["StationName"]
                    print("found station: ", rawLine["StationName"])
                elif "StationName" in rawLine and rawLine["StationName"].startswith("$EXT_PANEL_") and "StarSystem" in rawLine:
                    self.uniqueStations[rawLine["MarketID"]] = rawLine["StarSystem"] + ": " + rawLine["StationName"].split("$EXT_PANEL_",1)[1]
                if event in line:
                    print("Found landing ",lineCount)
                    if(rawLine.get(uniqueId) not in self.uniqueIDs): #it's a new market ID we want
                        print("ID is: ",rawLine.get(uniqueId))
                        self.firstInstanceInFile[rawLine.get(uniqueId)] = str(logfile)
                        print("Upate with Logfile: "+ str(logfile))
                        self.uniqueIDs.append(rawLine.get(uniqueId))
                        self.data[rawLine.get(uniqueId)] = rawLine
                    #only update if id and filename are still the same as first find
                    if(rawLine.get(uniqueId) in self.uniqueIDs):
                        if(rawLine.get(uniqueId) in self.firstInstanceInFile):
                            if(self.firstInstanceInFile[rawLine.get(uniqueId)] == str(logfile)):
                                print("getting latest version")
                                self.data[rawLine.get(uniqueId)] = rawLine

        for key in list(self.uniqueStations.keys()):
            if key not in self.uniqueIDs:
                del self.uniqueStations[key]
        with open("allColonyLandings.txt", "w") as f:
            f.write("\n".join(map(str, self.data.values())))
        if os.path.exists("resourceNotes.txt") and os.path.getsize("resourceNotes.txt") > 0:
            with open("resourceNotes.txt", "rb") as f:
                notesFromFile = pickle.load(f)
                print("The notes: ", notesFromFile)

        # create current project notes
        if self.notesLabels:
            if self.projectID not in self.notesBoxes:
                self.notesBoxes[self.projectID] = {}
            for note in self.notesLabels:
                print("Looping through note: "+ note+ ": " +self.notesLabels[note].text())
                if self.notesLabels[note].text() != "":
                    print("notes entered in now: ", self.notesLabels[note].text())
                    self.notesBoxes[self.projectID][note] = self.notesLabels[note].text()
                else:
                    print("nothing entered in note currently")
                    self.notesBoxes[self.projectID][note] = ""
        print("printing to file: ",self.notesBoxes)
        with open("resourceNotes.txt", "wb") as f:
            pickle.dump(self.notesBoxes, f, protocol=2)
        print("******Lines in current logfile:*******", lineCount)
        self.needsToReverse[self.sortType] = not self.needsToReverse[self.sortType]
        populateTable(self, self.sortType, self.hideFinished.isChecked(), self.tableSize.currentIndex())

def findShips(self):
    #"event":"Loadout"
    print("Loading Ships")

    for logfile in self.logFileListSorted:
        with open(logfile, "r", encoding='iso-8859-1') as f:
            for line in f:
                rawLine = json.loads(line)
                if "Ship" in rawLine and "CargoCapacity" in rawLine and "ShipIdent" in rawLine:
                    self.loadouts[rawLine["CargoCapacity"]] = rawLine["Ship"], rawLine["ShipIdent"]
                    print("Found new: ",rawLine["Ship"])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setStyleSheet("background-color: black;")
    window.show()
    sys.exit(app.exec())
