from dataclasses import dataclass, field
import enum
import glob
from pathlib import Path

from src.fetchers.Fetcher_local import getInstalledLib, fetchLocalLib
from src.generators.CMakeLibGenerator import cmakeifyLib
from src.parsers.CMakeParsing import  collectFilePaths, collectGeneratedConfigs, gatherTargetsFromConfigFiles, parseLib

from src.fetchers.Fetcher_github import fetchGithubRepo
from src.structs.PersistantDataManager import DepDat, PersistantDataManager, getCpppcDir
from .CMakeDataHelper import *
from .CppDataHelper import *
from .ProjectConfigurationData import *
import os

class LibrarySetupType(enum.Enum):
    Undefined   = 0
    BareBores   = 1
    CMakeBased  = 2
    InstalledCMake  = 3
    MakeBased   = 4

@dataclass
class CPPPC_Manager:
    cmakeListDat    : CMakeDataHelper
    cmake_inputsDat : CMakeDataHelper
    cppDat          : CppDataHelper
    projDat         : ProjectConfigurationGUI
    projDat_data    : ProjectConfigurationData
    
    
    def __init__(self, projdat : ProjectConfigurationGUI):
        self.projDat = projdat        
        self.cmakeListDat       = CMakeDataHelper()
        self.cmake_inputsDat    = CMakeDataHelper()        
        self.cppDat             = CppDataHelper(self.projDat, self.cmakeListDat)
        self.__setDefaultValues()
        self.projDat_data       = self.projDat.getData()
        self.decideOrder()

    def runtimeInit(self):        
        self.__setDefaultValues()
        self.projDat_data.update(self.projDat.getData())
        self.cmakeListDat.runtimeInit(self.projDat_data)
        self.cmake_inputsDat.runtimeInit(self.projDat_data)
        self.cppDat.runtimeInit()
        self.decideOrder()        
        
    def __prepareRequiredStructure(self):
        print("Iniitializing default values") 
        self.runtimeInit()

        print("Generating Directories")
        self.__generateDirectories()

        print("Adding user Configurations")
        self.projDat.initExtraFeatures()

    def createProject(self):     

        self.__prepareRequiredStructure()

        print("Setting up libraries")
        self.__setupLibraries()
        print("Creating Project")                
        self.projDat_data.update(self.projDat.getData()) #Update data inside...
        PersistantDataManager().addData(self.projDat_data)
        self.__generateCMakeLists()
        self.__generateCPPFiles()        

    def decideOrder(self):
        self.cmakeListDat.appendOrder(CMC_cmake_minimum_required)
        self.cmakeListDat.appendOrder(CMC_project)
        self.cmakeListDat.appendOrder(CMC_include)
        self.cmakeListDat.appendOrder(CMC_add_subdirectory)
        self.cmakeListDat.appendOrder(CMC_set)
        self.cmakeListDat.appendOrder(CMC_find_package)
        self.cmakeListDat.appendOrder(CMC_find_program)
        self.cmakeListDat.appendOrder(CMCC_if)
        self.cmakeListDat.appendOrder(CMC_file)
        self.cmakeListDat.appendOrder(CMC_add_executable)
        self.cmakeListDat.appendOrder(CMC_set_property)
        self.cmakeListDat.appendOrder(CMC_set_target_properties)
        self.cmakeListDat.appendOrder(CMC_target_sources)
        self.cmakeListDat.appendOrder(CMC_target_compile_options)
        self.cmakeListDat.appendOrder(CMC_target_link_options)
        self.cmakeListDat.appendOrder(CMC_target_include_directories)
        self.cmakeListDat.appendOrder(CMC_target_link_libraries)
        self.cmakeListDat.appendOrder(CMC_CALLFUNC)

        
    def __setDefaultValues(self):
        #TODO: Make placeholderAsBackup a behavior of a class rather than forced here...
        self.__placeholderAsBackup(self.projDat.projectTargetDir.widget, self.projDat.projectTargetDir.widget.placeholderText())    
        
        self.__placeholderAsBackup(self.projDat.projectName.widget, self.projDat.projectName.widget.placeholderText())    

        self.__placeholderAsBackup(self.projDat.projectExecName.widget, self.projDat.projectExecName.widget.placeholderText())
        
        self.__placeholderAsBackup(self.projDat.entryPointFile.widget, self.projDat.entryPointFile.widget.placeholderText())
    
    def __generateDirectories(self):
        if os.path.exists(self.projDat.getTargetPath()) and not self.projDat.overwriteProjectTargetDir.getState():
            print("Target Already exists")
            return
        else:
            os.makedirs(self.cmakeListDat.targetDirPath, exist_ok=True)
            os.makedirs(self.projDat.getPathInTarget(self.cmakeListDat.srcDirPath),    exist_ok=True)
            os.makedirs(self.projDat.getPathInTarget(self.cmakeListDat.cmakeDirPath),  exist_ok=True)
            os.makedirs(self.projDat.getPathInTarget(self.cmakeListDat.depsDirPath),   exist_ok=True)

    def __generateCMakeLists(self):

        self.cmakeListDat.genStr_cmake_min_version()
        self.cmakeListDat.genStr_cmake_projectdetails()

        # TODO: Generate a check for non-local libraries, i.e. libraries the user needs to install
        #       If any of these are missing, cancel configuration and message the user! 
        
        if(self.projDat.useProgram_ccache.getState()):
            self.cmakeListDat.addCMakeCompilerLauncher("ccache")

        self.cmakeListDat.genStr_cmake_find_packages()

        self.cmakeListDat.genStr_cmake_sourceDirVar()
        self.cmakeListDat.genStr_cmake_sources()
        self.cmakeListDat.genStr_cmake_headers()

        self.cmakeListDat.genStr_addExecutable()
        self.cmakeListDat.genStrHlp_addingProjectsTargetSources()
        
        if(self.projDat.useMeasureCompiletime.getState()):
            self.cmakeListDat.genStr_compileTimeProperty()

        self.cmakeListDat.genStr_cppProperties()

        self.cmakeListDat.genStr_targetIncludeDirectories()

        self.cmakeListDat.genStr_targetLinkLibraries()            

        self.createFileOnDemand("CMakeLists.txt",self.cmakeListDat.genCMakeList(), self.projDat_data.overwriteProjectTargetDir)

            
    def requireCMakeCppBridge(self):
        self.cmakeListDat.genStr_includeCmakeFile(self.cmakeListDat.FILE_cmake_cpp_data)
        self.cmakeListDat.genStr_callFunction(
            CMFUNC__add_cmake_inputs_to_targets, 
            [
                self.projDat.projectExecName_str(),
            ]
        )
        
        self.__generateCMakeCppBridge()

    def __generateCMakeCppBridge(self):
        self.__createCMakeFileOnDemand(
            self.cmake_inputsDat, self.projDat.overwriteProjectTargetDir.getState(), 
            self.cmake_inputsDat.FILE_cmake_cpp_data, 
            self.cmake_inputsDat.genStr_FILE_cmake_cpp_data())

        self.__createCMakeFileOnDemand(
            self.cmake_inputsDat, self.projDat.overwriteProjectTargetDir.getState(), 
            self.cmake_inputsDat.FILE_cmake_inputs_h_in, 
            self.cmake_inputsDat.genStr_FILE_cmake_inputs_h_in())

    def __generateCPPFiles(self):
        self.cppDat.genStr_FILE_entrypoint()
        self.cppDat.createCppEntryPointFileOnDemand()
        

    def __createCMakeFileOnDemand(self, cmakeFileDat :CMakeDataHelper, shouldOverwrite :bool, fileName : str, content :str ):
        if os.path.exists(cmakeFileDat.getRelativeCMakeFilePath(fileName)) and not shouldOverwrite:
            print(f"Target File ({cmakeFileDat.getRelativeCMakeFilePath(fileName)}) Already exists")
        else: 
            with open(cmakeFileDat.getRelativeCMakeFilePath(fileName), "w") as file:                        
                file.write(content)    

    def createFileOnDemand(self, fileName : str, content :str, shouldOverwrite :bool = False):
        if os.path.exists(self.projDat.getPathInTarget(fileName)) and not shouldOverwrite:
            print(f"Target File ({self.projDat.getPathInTarget(fileName)}) Already exists")
        else: 
            with open(self.projDat.getPathInTarget(fileName), "w") as file:                        
                file.write(content)

    def __setupLibraries(self):
        self.__fetchLibraries()
        print("Setup Libraries")
        for (name, lib) in self.projDat.linkLibs_dict.items():

            localLibPath = self.cmakeListDat.getLocalPathInDeps(name)
            targetLibPath = self.cmakeListDat.getPathInTarget(localLibPath) #TODO: Might not work if user use another directory than '.' for target dir...
            
            librarySetupType = self.__detectLibrarySetupType(name, lib)

            if librarySetupType == LibrarySetupType.InstalledCMake:
                # lib.targetNames = getInstalledLib(lib.getLibraryPath())     #TODO: Check if this can be replaced...
                lib.targetDatas = parseLib(lib.getLibraryPath())
                # TODO: Add Support for Windows and MacOS...            
                
            elif librarySetupType == LibrarySetupType.CMakeBased:

                self.cmakeListDat.genStr_addSubdirectory(localLibPath)
                if not PersistantDataManager().checkDependencyExist(os.path.abspath(targetLibPath)):

                    cmakedirPath = os.path.abspath(os.path.join(targetLibPath,"cmake" ))
                    finder_tempPath = Path.joinpath(getCpppcDir(), "temp_lib")
                    
                    # Copy necesary files to search through                     
                    confFiles = collectGeneratedConfigs(targetLibPath) 
                    confFiles.extend(collectFilePaths([],[cmakedirPath]))

                    targetDatas = gatherTargetsFromConfigFiles(confFiles, finder_tempPath.absolute().__str__())
                    lib.targetDatas = targetDatas

                    if lib.selectedTargets != None: 
                        PersistantDataManager().addDependencyData(DepDat(os.path.abspath(targetLibPath),lib.selectedTargets, lib.targetDatas))
                    else: 
                        WarnUser(f"Could not find targets for dependency at {os.path.abspath(targetLibPath)}")
                else:
                    tempDat = PersistantDataManager().getDependencyData(os.path.abspath(targetLibPath))
                    lib.selectedTargets = tempDat.targets
                    lib.targetDatas = tempDat.targetDatas
                    

            elif librarySetupType == LibrarySetupType.MakeBased:
                pass 
            elif librarySetupType == LibrarySetupType.BareBores:
                targetname, cmakeListFile = cmakeifyLib(targetLibPath)
                lib.selectedTargets = [targetname]

                if lib.selectedTargets != None: 
                    TEMP= TargetDatas([targetname],[],[],[]) #TODO, make sure that cmakeifyLib returns keyWords...
                    lib.targetDatas = TEMP
                    PersistantDataManager().addDependencyData(DepDat(os.path.abspath(targetLibPath),lib.selectedTargets, TEMP))
                else: 
                    WarnUser(f"Could not find targets for dependency at {os.path.abspath(targetLibPath)}")
                # Analyze: 
                    # 1: Glob recurse on All files, 

                # Type 1 header only: What is in the root? are there only header files No include or Src dir? 
                                
                # Type 3 headers + source: Is there a src dir, is there a include dir? is there a headers dir? *Go through common directory names : src, source, sources, sourcefiles, include, inc, includes*
                print("TODO Fix Barebones")
                
            else:
                
                WarnUser(str.format("Provided library is not installed or has a faulty path! \n\tName: {}\n\tPath: {}",name,lib.getLibraryPath()))

        if self.projDat_data.linkLibs != None:
            def refreshOverriddenDict(overrideDict:dict,guiDict:dict):

                newOverriddenDict = dict( ) 
                for addedLib in overrideDict.keys():
                    if addedLib in guiDict.keys():
                        newOverriddenDict[addedLib] = overrideDict[addedLib]
                overrideDict.clear()
                overrideDict.update(newOverriddenDict)

            refreshOverriddenDict(self.projDat_data._linkLibs_public_override, self.projDat_data.linkLibs)
            refreshOverriddenDict(self.projDat_data._linkLibs_private_override, self.projDat_data.linkLibs)
            refreshOverriddenDict(self.projDat_data._linkIncl_public_override, self.projDat_data.linkLibs)
            refreshOverriddenDict(self.projDat_data._linkIncl_private_override, self.projDat_data.linkLibs)
                        


            
        
    def __detectLibrarySetupType(self, name:str, lib: library_inputWidget) -> LibrarySetupType:
        detectedType : LibrarySetupType = LibrarySetupType.Undefined
        libraryPath = self.cmakeListDat.getLocalPathInDeps(name)
        
        installedLibs = getInstalledLib(lib.getLibraryPath())
        if len(installedLibs) > 0:
            detectedType = LibrarySetupType.InstalledCMake
        elif self.__checkFileExists(self.cmakeListDat.getPathInTarget(os.path.join(libraryPath, "CMakeLists.txt"))):
            detectedType = LibrarySetupType.CMakeBased
        elif self.__checkFileExists(self.cmakeListDat.getPathInTarget(os.path.join(libraryPath, "Makefile"))):
            detectedType = LibrarySetupType.MakeBased
        elif self.__checkFileExists(self.cmakeListDat.getPathInTarget(libraryPath)):
            detectedType = LibrarySetupType.BareBores

        return detectedType
    def __checkFileExists(self, pathToFile: str) -> bool:
        return os.path.exists(pathToFile)
        
    def __checkWildcardFileExists(self, pathToFile: str) -> bool: # TODO: Unused helper Func, consider deprecate
        matches = glob.glob(pathToFile)
        if len(matches) > 1: 
            terminate("Function only design to handle cases where there's one result from wildcard")
        return os.path.exists(matches[0]) if len(matches) != 0 else False
    
    def __getWildcardFile(self, pathToFile: str) -> str:  # TODO: Unused helper Func, consider deprecate
        matches = glob.glob(pathToFile)
        if len(matches) > 1: 
            terminate("Function only design to handle cases where there's one result from wildcard")
        return matches[0]

    def __fetchLibraries(self):        
        print("Fetching libraries")
        for (name, lib) in self.projDat.linkLibs_dict.items():            

            if lib.remote.getState():
                # Analyze Path type, local path or Url-> github/ other
                # if github path, use github fetch 
                fetchGithubRepo(lib.getLibraryPath(), name, self.projDat.getPathInTarget(self.cmakeListDat.depsDirPath))
            else: 
                fetchLocalLib(lib.getLibraryPath(), name, self.projDat.getUserProvidedLocalLibsPath(), self.projDat.getPathInTarget(self.cmakeListDat.depsDirPath))


        print("All libraries fetched")

    def configureLibraries(self, layout_projectName):
        parentL = QHBoxLayout()
        layout, groupWidget = hlp.addFloatingWindow(parentL, "Library Configuration")
        self.projDat_data.update(self.projDat.getData())
        self.__prepareRequiredStructure()
        self.__setupLibraries() 
        self.projDat_data.update(self.projDat.getData())
        if self.projDat_data.linkLibs != None:
            grid = QGridLayout()

            FOLD_SYMBOL   = "►"    # Unicode symbol for fold arrow
            UNFOLD_SYMBOL = "▼"    # Unicode symbol for unfold arrow

            currentRow = 0
            groupCount = 0
            for libDirName, libdat in self.projDat_data.linkLibs.items():
                libraryGroup = QGroupBox()                

                innerGrid = QGridLayout()
                libName = libdat[0]
                publ    = libdat[1] 
                defTargets   = libdat[2] 
                targetDat    = libdat[3]                 

                libLabel = QLabel()
                libLabel.setText(libName)                              
                
                innerGrid.addWidget(libLabel,currentRow,0)
                currentRow+=1

                def hide(group : QGroupBox, label :QLabel):                    
                    if not group.isHidden():
                        label.setText(f"{FOLD_SYMBOL} "+label.text()[1:])
                        group.setHidden(True)
                    else :
                        group.setHidden(False)
                        label.setText(f"{UNFOLD_SYMBOL} "+label.text()[1:])


                linking_group = QGroupBox()
                linking_group.setHidden(True)
                linking_group_label = QLabel()

                selectedFoldStatus = FOLD_SYMBOL
                numOfTargets = self.__getNumberOfTargets(targetDat)
                if numOfTargets > 0:
                    selectedFoldStatus = UNFOLD_SYMBOL
                    linking_group.setHidden(False)

                linking_group_label.setText(f"{selectedFoldStatus} <a href=\"linking_group\">Select Library Targets through parsed Target names</a> [{numOfTargets} Found]")
                linking_group_label.linkActivated.connect(lambda checked, group=linking_group, label=linking_group_label : hide(group, label))
                linking_group.setFlat(True)
                
                linking_group_layout = QVBoxLayout()
                linking_group.setLayout(linking_group_layout)
                
                allLibs = self.__prepareAllDefinedLibs(defTargets,libDirName)

                libs_1 = QLineEdit()
                libs_2 = QLineEdit()
                self.addconf_libraryLinking(libs_1, [libs_2],allLibs,currentRow, targetDat, publ, linking_group_layout, libDirName)
                
                keyword_group = QGroupBox()
                keyword_group.setHidden(True)
                selectedFoldStatus = FOLD_SYMBOL
                numOfTargets = self.__getNumberOfKeywords(targetDat)
                if numOfTargets > 0:
                    selectedFoldStatus = UNFOLD_SYMBOL
                    keyword_group.setHidden(False)

                keyword_group_label = QLabel()
                keyword_group_label.setText(f"{selectedFoldStatus} <a href=\"keyword_group\">Select Library and Includes through parsed Keywords</a>  [{numOfTargets} Found]")
                keyword_group_label.linkActivated.connect(lambda checked, group=keyword_group, label=keyword_group_label : hide(group,label))
                include_group_layout = QVBoxLayout()
                keyword_group.setLayout(include_group_layout)
                keyword_group.setFlat(True)
                self.addconf_includes(libs_2, [libs_1], allLibs, currentRow, targetDat, publ, include_group_layout, libDirName)
                
                
                innerGrid.addWidget(keyword_group_label)
                innerGrid.addWidget(keyword_group)
                innerGrid.addWidget(linking_group_label)
                innerGrid.addWidget(linking_group)
                libraryGroup.setLayout(innerGrid)
                groupCount += 1
                grid.addWidget(libraryGroup)
                
            layout.addLayout(grid)

    def __getNumberOfTargets(self, targetDatas:TargetDatas):
        targetTypes = [
                    targetDatas.STATIC,
                    targetDatas.SHARED,
                    targetDatas.INTERFACE,
                    targetDatas.possibleTargets
                ]
        return sum( len(current) for current in targetTypes)
    
    def __getNumberOfKeywords(self, targetDatas:TargetDatas):
        
        return 0 if targetDatas.keyWords == None else len(targetDatas.keyWords.items())

    def addconf_includes(self,libs_lineEdit:QLineEdit,allLibsLineEdits:list[QLineEdit], allLibs:list[str], currentRow, targetDat, public:bool, include_group_layout, libDirName:str):
        includes_lineEdit = QLineEdit()
        allLibIncldues = self.__prepareAllDefinedLibIncludes(libDirName)
        includes_lineEdit.setText(",".join(t for t in allLibIncldues))

        libs_lineEdit.setText(",".join(t for t in allLibs))

        def toggleLib(includeName, lineEdit):
            lineEdit_list = [lib.strip() for lib in lineEdit.text().strip().split(",")if lib != ""]                
            if includeName.strip() in lineEdit_list: 
                lineEdit_list.remove(includeName.strip())
                
            else: 
                lineEdit_list.append(includeName)
            lineEdit.setText(", ".join(lineEdit_list))
            for le in allLibsLineEdits:
                le.setText(", ".join(lineEdit_list))
            

        def toggleInclude(includeName, lineEdit):
            lineEdit_list = [lib.strip() for lib in lineEdit.text().strip().split(",")if lib != ""]                
            if includeName.strip() in lineEdit_list: 
                lineEdit_list.remove(includeName.strip())
                
            else: 
                lineEdit_list.append(includeName)
            lineEdit.setText(", ".join(lineEdit_list))            


        MAX_VARS_PER_ROW = 2
        keywordList :list[str] = [k for k in targetDat.keyWords.keys()] if targetDat.keyWords != None else []
        if targetDat.includes != None:
            for m in targetDat.includes: 
                if not m in keywordList:
                    keywordList.append(m)

        keyWords = [
                    ("Identifed CMake\nProject Variables",keywordList),
                ]
            
        for keyWordDict in keyWords:        
            targetTypeGroup = QGroupBox()
            targetTypeGroupLayout = QGridLayout()
            targetTypeGroup.setLayout(targetTypeGroupLayout)
            include_group_layout.addWidget(targetTypeGroup)

            currentTargetType = QLabel()
            currentTargetType.setText(str.format("{}:",keyWordDict[0]))
            subGrid = QGridLayout()

            targetTypeGroupLayout.addWidget(currentTargetType,currentRow,0)                    
            currentRow += 1

            targetTypeGroupLayout.addLayout(subGrid, currentRow, 0)

            targetCounter = 0
            if keyWordDict[1] == None or len(keyWordDict[1]) == 0:
                no_identified_targets = QLabel()
                no_identified_targets.setText("No Identified CMake Project Variables")
                subGrid.addWidget(no_identified_targets, currentRow, 0)
                            
            else : 
                BUTTON_WIDTH = 50
                def addHeader(currentRow : int, column : int):
                    varLayoutHeader = QGridLayout()
                    varButtonLayoutHeader = QHBoxLayout()
                    titleHeader = QLabel("Identified Keyword")
                    incHeader = QLabel("Add\nInclude")
                    libHeader = QLabel("Add\nLibrary")
                    titleHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    incHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    libHeader.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    incHeader.setMaximumWidth(BUTTON_WIDTH)           
                    libHeader.setMaximumWidth(BUTTON_WIDTH)           
                    varLayoutHeader.addWidget(titleHeader,currentRow, 0)
                    varLayoutHeader.addLayout(varButtonLayoutHeader,currentRow, 1)
                    varButtonLayoutHeader.addWidget(incHeader)
                    varButtonLayoutHeader.addWidget(libHeader)
                    
                    subGrid.addLayout(varLayoutHeader,currentRow, column)                    
                    
                headerColumn = 0
                while headerColumn <  MAX_VARS_PER_ROW:
                    addHeader(currentRow, headerColumn)
                    headerColumn +=1
                currentRow += 1
                
                for target in keyWordDict[1]:
                    varLayout = QGridLayout()                    
                    varButtonLayout = QHBoxLayout()                                        
                    
                    varLabel = QLabel(target)
                    varLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    var_inc_button = QPushButton("+/-")
                    var_inc_button.setMaximumWidth(BUTTON_WIDTH)
                    var_lib_button = QPushButton("+/-")
                    var_lib_button.setMaximumWidth(BUTTON_WIDTH)
                    varButtonLayout.addWidget(var_inc_button)
                    varButtonLayout.addWidget(var_lib_button)                    
                                
                    column = targetCounter%MAX_VARS_PER_ROW

                    varLayout.addWidget(varLabel, currentRow,0)
                    varLayout.addLayout(varButtonLayout,currentRow,1)
                    subGrid.addLayout(varLayout,currentRow, column)

                    currentRow += math.floor((column+1)/MAX_VARS_PER_ROW)

                    var_inc_button.clicked.connect(lambda checked, target=target, includes_lineEdit=includes_lineEdit:toggleInclude(target,includes_lineEdit))
                    var_lib_button.clicked.connect(lambda checked, target=target, libs_lineEdit=libs_lineEdit:toggleLib(target,libs_lineEdit))
                    targetCounter +=1
                                                            
            currentRow+=1


        def onLibEditFinish(lineEdit :QLineEdit, libName:str, public:bool):
            if (public):
                self.projDat_data._linkLibs_public_override[libName] = [lib.strip() for lib in lineEdit.text().strip().split(",") if lib != ""]
            else:
                self.projDat_data._linkLibs_private_override[libName] = [lib.strip() for lib in lineEdit.text().strip().split(",") if lib != ""]

        libs_lineEdit.textChanged.connect(
            lambda checked, lineEdit=libs_lineEdit ,libname=libDirName, publ=public: onLibEditFinish(lineEdit, libname,publ)
        )

        def onLibInclFinish(lineEdit :QLineEdit, libName:str, public:bool):
            if (public):
                self.projDat_data._linkIncl_public_override[libName] = [lib.strip() for lib in lineEdit.text().strip().split(",") if lib != ""]
            else:
                self.projDat_data._linkIncl_private_override[libName] = [lib.strip() for lib in lineEdit.text().strip().split(",") if lib != ""]

        includes_lineEdit.textChanged.connect(
            lambda checked, lineEdit=includes_lineEdit ,libname=libDirName, publ=public: onLibInclFinish(lineEdit, libname,publ)
        )

        selectedIncludes = QLabel()
        selectedIncludes.setText("Selected Includes:")
        include_group_layout.addWidget(selectedIncludes)
        include_group_layout.addWidget(includes_lineEdit)           
        currentRow += 1
        selectedLibraries = QLabel()
        selectedLibraries.setText("Selected Libraries:")
        include_group_layout.addWidget(selectedLibraries)           
        include_group_layout.addWidget(libs_lineEdit)           
        currentRow += 1

    def __prepareAllDefinedLibs(self,defSelectedTarget:list[str],libDirName:str) -> list[str]:
        usersLibs :list[str] = []
        
        
        if len(self.projDat_data._linkLibs_public_override) > 0:
            if libDirName in self.projDat_data._linkLibs_public_override:
                usersLibs.extend(self.projDat_data._linkLibs_public_override[libDirName])
        if len(self.projDat_data._linkLibs_private_override) > 0: 
            if libDirName in self.projDat_data._linkLibs_private_override:
                usersLibs.extend(self.projDat_data._linkLibs_private_override[libDirName])

        if len(usersLibs) == 0: 
            usersLibs = defSelectedTarget
        return usersLibs
    
    def __prepareAllDefinedLibIncludes(self,libDirName:str) -> list[str]:
        usersLibIncludes :list[str] = []
                
        if len(self.projDat_data._linkIncl_public_override) > 0:
            if libDirName in self.projDat_data._linkIncl_public_override:
                usersLibIncludes.extend(self.projDat_data._linkIncl_public_override[libDirName])
        if len(self.projDat_data._linkIncl_private_override) > 0: 
            if libDirName in self.projDat_data._linkIncl_private_override:
                usersLibIncludes.extend(self.projDat_data._linkIncl_private_override[libDirName])
        
        return usersLibIncludes

    def addconf_libraryLinking(self, linkTargets_lineEdit:QLineEdit,allLibsLineEdits:list[QLineEdit], allLibs:list[str],currentRow:int,targetDat:TargetDatas,public:bool, linking_group_layout, libDirName:str):
        
        confirmedComponents = targetDat.parsedComponentTargets

        componentsLayout = QHBoxLayout()
        componentTarget_label = QLabel()
        componentsOfTarget_label = QLabel()
        componentTarget_lineEdit = QLineEdit()
        componentsOfTarget_lineEdit = QLineEdit()
        componentTarget_label.setText("Installed Target:")
        componentsOfTarget_label.setText("Components:")
        if libDirName in self.projDat_data._linkLibs_findPackage and self.projDat_data._linkLibs_findPackage[libDirName] != "": 
            componentTarget_lineEdit.setText(self.projDat_data._linkLibs_findPackage[libDirName])
        elif targetDat.find_package != None:
            componentTarget_lineEdit.setText(targetDat.find_package)
        else :             
            componentTarget_lineEdit.setPlaceholderText("Leave empty if no components based or local lib")

        def toggleLibTarget(targetName :str, libs_lineEdit :QLineEdit, findTarget_lineEdit :QLineEdit,components_lineEdit:QLineEdit,confirmedComponents:list[str]):
            lib_lineLibs = [lib.strip() for lib in libs_lineEdit.text().strip().split(",")if lib != ""]
            lib_linkComp = [lib.strip() for lib in components_lineEdit.text().strip().split(",")if lib != ""]
            findTargetName = findTarget_lineEdit.text()

            def isComponent(findTargetName:str, targetName:str,confirmedComponents:list[str])->bool:
                if targetName not in confirmedComponents:
                    return False 
                targetName_regx = re.compile(fr"^{findTargetName}(?:-|::)(.*)", re.IGNORECASE)
                nameMatch = re.match(targetName_regx,targetName)
                return nameMatch != None and nameMatch[1] != findTargetName

            if targetName.strip() in lib_lineLibs: 
                lib_lineLibs.remove(targetName.strip())
                if isComponent(findTargetName, targetName, confirmedComponents):                    
                    startIndex = targetName.strip().upper().find(findTargetName.upper())
                    endIndex = startIndex + len(findTargetName)
                    fullTargetComponent = targetName.strip()[endIndex:]
                    compnentSeperator_regx = re.compile("^(?:-|::)(.*)")
                    cleanedComponentStr = re.findall(compnentSeperator_regx, fullTargetComponent)[0]
                    if cleanedComponentStr in lib_linkComp:
                        lib_linkComp.remove(cleanedComponentStr)                
            else: 
                lib_lineLibs.append(targetName)
                if isComponent(findTargetName, targetName, confirmedComponents):                    
                    startIndex = targetName.upper().find(findTargetName.upper())
                    endIndex = startIndex + len(findTargetName)
                    fullTargetComponent = targetName[endIndex:]
                    compnentSeperator_regx = re.compile("^(?:-|::)(.*)")
                    cleanedComponentStr = re.findall(compnentSeperator_regx, fullTargetComponent)[0]
                    lib_linkComp.append(cleanedComponentStr)

            libs_lineEdit.setText(", ".join(lib_lineLibs))
            components_lineEdit.setText(", ".join(lib_linkComp))
            for le in allLibsLineEdits:
                le.setText(", ".join(lib_lineLibs))

        # Initialize previous stored library data...
        for l in allLibs:
            toggleLibTarget(l, linkTargets_lineEdit, componentTarget_lineEdit, componentsOfTarget_lineEdit, confirmedComponents)

        MAX_TARGETS_PER_ROW = 4

        targetTypes = [
                    ("STATIC",targetDat.STATIC),
                    ("SHARED",targetDat.SHARED),
                    ("INTERFACE",targetDat.INTERFACE) ,
                    ("Possible\nTargets",targetDat.possibleTargets)
                ]
            
        for targetType in targetTypes:
            targetTypeGroup = QGroupBox()
            targetTypeGroupLayout = QGridLayout()
            targetTypeGroup.setLayout(targetTypeGroupLayout)
            linking_group_layout.addWidget(targetTypeGroup)

            currentTargetType = QLabel()
            currentTargetType.setText(str.format("{}:",targetType[0]))
            subGrid = QGridLayout()

            targetTypeGroupLayout.addWidget(currentTargetType,currentRow,0)                    
            targetTypeGroupLayout.setColumnStretch(1,10)
            targetTypeGroupLayout.setColumnMinimumWidth(0,65)
            targetTypeGroupLayout.addLayout(subGrid, currentRow, 1)
            targetCounter = 0
            if len(targetType[1]) == 0: 
                no_identified_targets = QLabel()
                no_identified_targets.setText("No Identified Target")
                subGrid.addWidget(no_identified_targets, currentRow, 0)
                        
            else: 
                for target in targetType[1]:
                    toggleTargetButton = QPushButton(target)

                    column = targetCounter%MAX_TARGETS_PER_ROW
                    subGrid.addWidget(toggleTargetButton, currentRow, column)

                    currentRow += math.floor((column+1)/MAX_TARGETS_PER_ROW)
                    toggleTargetButton.clicked.connect(
                        lambda checked, 
                        target=target, 
                        libs_lineEdit=linkTargets_lineEdit,
                        findTarget_lineEdit=componentTarget_lineEdit,
                        components_lineEdit=componentsOfTarget_lineEdit,
                        :toggleLibTarget(target,libs_lineEdit, findTarget_lineEdit,components_lineEdit, confirmedComponents))
                    targetCounter +=1
                                                            
            currentRow+=1

        selectedTargets = QLabel()
        selectedTargets.setText("Selected Targets:")

        selectedComponentTargets = QLabel()
        selectedComponentTargets.setText("Selected Find_packages Components:")

        componentsLayout.addWidget(componentTarget_label)
        componentsLayout.addWidget(componentTarget_lineEdit)
        componentsLayout.addWidget(componentsOfTarget_label)
        componentsLayout.addWidget(componentsOfTarget_lineEdit)

        def onEditFinish_lib(lineEdit :QLineEdit, libName:str, public:bool):
            if (public):
                self.projDat_data._linkLibs_public_override[libName] = [lib.strip() for lib in lineEdit.text().strip().split(",") if lib != ""]
            else:
                self.projDat_data._linkLibs_private_override[libName] = [lib.strip() for lib in lineEdit.text().strip().split(",") if lib != ""]
        
        def onEditFinish_comp(lineEdit :QLineEdit, libName:str):
            self.projDat_data._linkLibs_components[libName] = [lib.strip() for lib in lineEdit.text().strip().split(",") if lib != ""]

        def onComponentTargetFinish(target :QLineEdit, targets:QLineEdit, targets_comps:QLineEdit, libName:str):
            orig_targets = [lib.strip() for lib in targets.text().strip().split(",")if lib != ""]                
            newFindName :str = target.text()
            # Toggle off, to clear old components
            for l in orig_targets:
                toggleLibTarget(l, linkTargets_lineEdit, target, componentsOfTarget_lineEdit, confirmedComponents)
            
            # Manually remove contents of Components lineEdit
            targets_comps.setText("") 
            # Toggle On, to restore users choice of components (where applicable)
            for l in orig_targets:
                toggleLibTarget(l, linkTargets_lineEdit, target, componentsOfTarget_lineEdit, confirmedComponents)            
                
            self.projDat_data._linkLibs_findPackage[libName] = newFindName

        linkTargets_lineEdit.textChanged.connect(
            lambda checked, lineEdit=linkTargets_lineEdit ,libname=libDirName, publ=public: onEditFinish_lib(lineEdit, libname,publ)
        )
        componentsOfTarget_lineEdit.textChanged.connect(
            lambda checked, lineEdit=componentsOfTarget_lineEdit ,libname=libDirName: onEditFinish_comp(lineEdit, libname)
        )

        componentTarget_lineEdit.textChanged.connect(
            lambda checked, 
            lineEdit=componentTarget_lineEdit,
            targets=linkTargets_lineEdit,
            targets_comps=componentsOfTarget_lineEdit,
            libname=libDirName
            : onComponentTargetFinish(lineEdit, targets, targets_comps,libname)
        )
        
        linking_group_layout.addWidget(selectedTargets)
        linking_group_layout.addWidget(linkTargets_lineEdit)
        linking_group_layout.addWidget(selectedComponentTargets)
        linking_group_layout.addLayout(componentsLayout)
        currentRow += 1
                
    def createSanitizerBlacklistOnDemand(self):
        blacklistfile = "### lines with one # are examples...\n"
        blacklistfile += "### Ignore exactly this function (the names are mangled)\n" 
        blacklistfile += "# fun:MyFooBar\n" 
        blacklistfile += "### Ignore MyFooBar(void) if it is in C++:\n" 
        blacklistfile += "# fun:_Z8MyFooBarv\n" 
        blacklistfile += "### Ignore all function containing MyFooBar\n" 
        blacklistfile += "# fun:*MyFooBar*\n" 
        self.createFileOnDemand("sanitizer_blacklist.txt", blacklistfile, self.projDat.overwriteProjectTargetDir.getState())

    def __placeholderAsBackup(self, widget, placeholder:str):
        if(widget.text() == ""):
            widget.setText(placeholder)