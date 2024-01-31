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
        self.projDat_data       = ProjectConfigurationData()
        self.decideOrder()

    def runtimeInit(self):        
        self.__setDefaultValues()
        self.projDat_data = self.projDat.getData()
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
        self.cmakeListDat.appendOrder(CMC_find_program)
        self.cmakeListDat.appendOrder(CMCC_if)
        self.cmakeListDat.appendOrder(CMC_file)
        self.cmakeListDat.appendOrder(CMC_add_executable)
        self.cmakeListDat.appendOrder(CMC_set_property)
        self.cmakeListDat.appendOrder(CMC_set_target_properties)
        self.cmakeListDat.appendOrder(CMC_target_sources)
        self.cmakeListDat.appendOrder(CMC_target_compile_options)
        self.cmakeListDat.appendOrder(CMC_target_link_options)
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

        self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_cmake_min_version())
        self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_cmake_projectdetails())

        # TODO: Generate a check for non-local libraries, i.e. libraries the user needs to install
        #       If any of these are missing, cancel configuration and message the user! 
        
        if(self.projDat.useProgram_ccache.getState()):
            self.cmakeListDat.addToCMakeList(self.cmakeListDat.addCMakeCompilerLauncher("ccache"))

        self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_cmake_sourceDirVar())
        self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_cmake_sources())
        self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_cmake_headers())

        self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_addExecutable())
        self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStrHlp_addingProjectsTargetSources())
        
        if(self.projDat.useMeasureCompiletime.getState()):
            self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_compileTimeProperty())

        self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_cppProperties())

        self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_targetLinkLibraries())            

        with open(self.cmakeListDat.targetDirPath+"/"+"CMakeLists.txt", "w") as file:
            file.write(self.cmakeListDat.genCMakeList())
            
    def requireCMakeCppBridge(self):
        self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_includeCmakeFile(self.cmakeListDat.FILE_cmake_cpp_data))
        self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_callFunction(
            CMFUNC__add_cmake_inputs_to_targets, 
            [
                self.projDat.projectExecName_str(),
            ])
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

            # TODO: Move into each case...
            extraData = parseLib(os.path.basename(lib.getLibraryPath()))

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

                    targetDatas = gatherTargetsFromConfigFiles(confFiles, finder_tempPath.absolute().__str__())                      #NEW
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
            
        
    def __detectLibrarySetupType(self, name:str, lib: library_inputWidget) -> LibrarySetupType:
        detectedType : LibrarySetupType = LibrarySetupType.Undefined
        libraryPath = self.cmakeListDat.getLocalPathInDeps(name)
        
        installedLibs = getInstalledLib(lib.getLibraryPath())
        if len(installedLibs) > 0:
            detectedType = LibrarySetupType.InstalledCMake
        elif self.__checkFileExists(self.cmakeListDat.getPathInTarget(pathify(libraryPath, "CMakeLists.txt"))):
            detectedType = LibrarySetupType.CMakeBased
        elif self.__checkFileExists(self.cmakeListDat.getPathInTarget(pathify(libraryPath, "Makefile"))):
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
        layout = hlp.addFloatingWindow(parentL, "Library Configuration")
        self.projDat_data.update(self.projDat.getData())
        self.__prepareRequiredStructure()
        self.__setupLibraries() 
        self.projDat_data.update(self.projDat.getData())
        if self.projDat_data.linkLibs != None:
            grid = QGridLayout()
            
            currentRow = 0
            groupCount = 0
            for libDirName, libdat in self.projDat_data.linkLibs.items():
                group = QGroupBox()
                innerGrid = QGridLayout()
                libName = libdat[0]
                publ    = libdat[1] 
                targetDat    = libdat[3]                 

                libLabel = QLabel()
                libLabel.setText(libName)              

                libs_lineEdit = QLineEdit()
                def toggleLib(targetName, libs_lineEdit):
                    lib_lineLibs = [lib.strip() for lib in libs_lineEdit.text().strip().split(",")if lib != ""]                
                    if targetName.strip() in lib_lineLibs: 
                        lib_lineLibs.remove(targetName.strip())
                    else: 
                        lib_lineLibs.append(targetName)
                    libs_lineEdit.setText(", ".join(lib_lineLibs))

                
                innerGrid.addWidget(libLabel,currentRow,0)
                currentRow+=1
                
                MAX_TARGETS_PER_ROW = 4

                targetTypes = [
                    ("STATIC",targetDat.STATIC),
                    ("SHARED",targetDat.SHARED),
                    ("INTERFACE",targetDat.INTERFACE) ,
                    ("possibleTargets",targetDat.possibleTargets)
                ]
            
                for targetType in targetTypes:

                    currentTargetType = QLabel()
                    currentTargetType.setText(str.format("\t{}:",targetType[0]))
                    subGrid = QGridLayout()
                    
                    innerGrid.addWidget(currentTargetType,currentRow,0)
                    innerGrid.addLayout(subGrid, currentRow, 1)
                    targetCounter = 0
                    for target in targetType[1]:
                        
                        newButton = QPushButton(target)

                        column = targetCounter%MAX_TARGETS_PER_ROW
                        subGrid.addWidget(newButton, currentRow, column)

                        currentRow += math.floor((column+1)/MAX_TARGETS_PER_ROW)
                        newButton.clicked.connect(lambda checked, target=target, libs_lineEdit=libs_lineEdit:toggleLib(target,libs_lineEdit))
                        targetCounter +=1
                                                            
                    currentRow+=1
                
                selectedTargets = QLabel()
                selectedTargets.setText("\tSelected Targets:")
                
                innerGrid.addWidget(selectedTargets,currentRow,0)
                innerGrid.addWidget(libs_lineEdit,currentRow,1)                
                currentRow += 1
                group.setLayout(innerGrid)
                groupCount += 1
                grid.addWidget(group)
                
            layout.addLayout(grid)
                
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