from dataclasses import dataclass, field
import enum
import glob
from src.cmake_helper import configureCmakeProjectWithGraphviz, getLibraryTargetFromPCFile
from src.parsers.CMakeParsing import  getLibraryTargets

from src.fetchers.Fetcher_github import fetchGithubRepo
from .CMakeDataHelper import *
from .CppDataHelper import *
from .ProjectConfigurationData import *
import os

class LibrarySetupType(enum.Enum):
    Undefined   = 0
    BareBores   = 1
    CMakeBased  = 2
    MakeBased   = 3

@dataclass
class CPPPC_Manager:
    cmakeListDat    : CMakeDataHelper
    cmake_inputsDat : CMakeDataHelper
    cppDat          : CppDataHelper
    projDat         : ProjectConfigurationData
    
    
    def __init__(self, projdat : ProjectConfigurationData):
        self.projDat = projdat        
        self.cmakeListDat       = CMakeDataHelper(self.projDat)
        self.cmake_inputsDat    = CMakeDataHelper(self.projDat)
        self.cppDat             = CppDataHelper(self.projDat, self.cmakeListDat)
        self.decideOrder()

    def runtimeInit(self):        
        self.__setDefaultValues()
        self.cmakeListDat.runtimeInit()
        self.cmake_inputsDat.runtimeInit()
        self.cppDat.runtimeInit()
        self.decideOrder()        
        

    def createProject(self):     
        print("Iniitializing default values") 
        self.runtimeInit()

        print("Generating Directories")
        self.__generateDirectories()

        print("Adding user Configurations")
        self.projDat.initExtraFeatures()
                   
        print("Creating Project")        
        self.projDat.toString()     #TODO: Junk?!
        self.__setupLibraries()
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
            if librarySetupType == LibrarySetupType.CMakeBased:
                # step 1: Configure Project!  => Generate with --graphwiz to temp/t.dot
                configureCmakeProjectWithGraphviz(targetLibPath)

                self.cmakeListDat.genStr_addSubdirectory(localLibPath)
                
                if self.__checkWildcardFileExists(pathify(targetLibPath,"*.pc")):
                    # Alt 1:    check if *.pc was generated, use data from that OR *-targets.cmake 
                    pcFilePath = self.__getWildcardFile(pathify(targetLibPath,"*.pc"))
                    targetName = getLibraryTargetFromPCFile(pcFilePath)
                    lib.targetName = targetName
                    
                if lib.targetName == None :
                    # Alt 2:  Parse CMakeLists.txt, look for add_library; Consider Interface/Alias  
                        # => Create Library ? 
                        # => Add Library ? 
                        # => Add Include directories
                    libTargets = getLibraryTargets(targetLibPath)
                    #TODO! Let user pick which targets to include, if more than one...
                    lib.targetName = libTargets[0]
                    

            elif librarySetupType == LibrarySetupType.MakeBased:
                pass 
            elif librarySetupType == LibrarySetupType.BareBores:

                # Analyze: 
                    # 1: Glob recurse on All files, 

                # Type 1 header only: What is in the root? are there only header files No include or Src dir? 
                                
                # Type 3 headers + source: Is there a src dir, is there a include dir? is there a headers dir? *Go through common directory names : src, source, sources, sourcefiles, include, inc, includes*
                print("TODO Fix Barebones")
                
            else:
                terminate("LibrarySetupType is undefined!")
            
        
    def __detectLibrarySetupType(self, name:str, lib: library_inputWidget) -> LibrarySetupType:
        detectedType : LibrarySetupType = LibrarySetupType.BareBores
        libraryPath = self.cmakeListDat.getLocalPathInDeps(name)
        if self.__checkFileExists(self.cmakeListDat.getPathInTarget(pathify(libraryPath, "CMakeLists.txt"))):
            detectedType = LibrarySetupType.CMakeBased
        elif self.__checkFileExists(self.cmakeListDat.getPathInTarget(pathify(libraryPath, "Makefile"))):
            detectedType = LibrarySetupType.MakeBased

        return detectedType
    def __checkFileExists(self, pathToFile: str) -> bool:
        return os.path.exists(pathToFile)
        
    def __checkWildcardFileExists(self, pathToFile: str) -> bool:
        matches = glob.glob(pathToFile)
        if len(matches) > 1: 
            terminate("Function only design to handle cases where there's one result from wildcard")
        return os.path.exists(matches[0])
    
    def __getWildcardFile(self, pathToFile: str) -> str:
        matches = glob.glob(pathToFile)
        if len(matches) > 1: 
            terminate("Function only design to handle cases where there's one result from wildcard")
        return matches[0]

    def __fetchLibraries(self):
        print("Fetching libraries")
        for (name, lib) in self.projDat.linkLibs_dict.items():            
            fetchGithubRepo(lib.getLibraryPath(), name, self.projDat.getPathInTarget(self.cmakeListDat.depsDirPath))
        print("All libraries fetched")

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