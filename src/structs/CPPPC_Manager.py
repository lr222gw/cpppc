from dataclasses import dataclass, field
from .CMakeData import *
from .CppDataHelper import *
from .ProjectConfigurationData import *
import os

@dataclass
class CPPPC_Manager:
    cmakeListDat    : CMakeData
    cmake_inputsDat : CMakeData
    cppDat          : CppDataHelper
    projDat         : ProjectConfigurationData
    
    
    def __init__(self, projdat : ProjectConfigurationData):
        self.projDat = projdat        
        self.cmakeListDat       = CMakeData(self.projDat)
        self.cmake_inputsDat    = CMakeData(self.projDat)
        self.cppDat             = CppDataHelper(self.projDat, self.cmakeListDat)

    def runtimeInit(self):        
        self.__setDefaultValues()

    def createProject(self):     
        print("Iniitializing default values") 
        self.runtimeInit()

        print("Creating Project")        
        self.projDat.toString()     #TODO: Junk?!
        self.__generateCMakeLists()
        self.__generateCMakeCppBridge()
        self.__generateCPPFiles()
        
    def __setDefaultValues(self):
        #TODO: Make placeholderAsBackup a behavior of a class rather than forced here...
        self.__placeholderAsBackup(self.projDat.projectTargetDir.widget, self.projDat.projectTargetDir.widget.placeholderText())    
        
        self.__placeholderAsBackup(self.projDat.projectName.widget, self.projDat.projectName.widget.placeholderText())    

        self.__placeholderAsBackup(self.projDat.projectExecName.widget, self.projDat.projectExecName.widget.placeholderText())
        
        self.__placeholderAsBackup(self.projDat.entryPointFile.widget, self.projDat.entryPointFile.widget.placeholderText())
    
    def __generateCMakeLists(self):

        if os.path.exists(self.projDat.getTargetPath()) and not self.projDat.overwriteProjectTargetDir.getState():
            print("Target Already exists")
            return
        else:
            print("Target Will be Created")
            os.makedirs(self.cmakeListDat.targetDirPath, exist_ok=True)
            os.makedirs(self.cmakeListDat.getPathInTarget(self.cmakeListDat.srcDirPath),    exist_ok=True)
            os.makedirs(self.cmakeListDat.getPathInTarget(self.cmakeListDat.cmakeDirPath),  exist_ok=True)

            self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_cmake_min_version())
            self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_cmake_projectdetails())
            
            if(self.projDat.useProgram_ccache.getState()):
                self.cmakeListDat.addToCMakeList(self.cmakeListDat.addCMakeCompilerLauncher("ccache"))

            # if(projdata.useCmakeCppBridge.getState()): #TODO: FIX
            if(True): #TODO: FIX
                self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_includeCmakeFile(self.cmakeListDat.FILE_cmake_cpp_data))

            self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_cmake_sourceDirVar())
            self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_cmake_sources())
            self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_cmake_headers())

            self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_addExecutable())
            self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStrHlp_addingProjectsTargetSources())

            # if(self.projDat.useSanitizers.getState()):
            #     self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_compileSanitizers(self.projDat))
            #     self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_linkSanitizers(self.projDat))
            
            if(self.projDat.useMeasureCompiletime.getState()):
                self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_compileTimeProperty())

            self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_cppProperties())

            #TODO: Only add this line if users checked use CMakeToCpp Bridge...
            self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_callFunction(
                CMFUNC__add_cmake_inputs_to_targets, 
                [
                    self.projDat.projectExecName_str(),
                ])
            )

            self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_targetLinkLibraries())            

            with open(self.cmakeListDat.targetDirPath+"/"+"CMakeLists.txt", "w") as file:
                file.write(self.cmakeListDat.genCMakeList())
            #TODO: Move other file creation below creation of CMakeLists.txt 
            
    
    def __generateCMakeCppBridge(self):
        # if(projdata.useCmakeCppBridge.getState()):     
        if(True): #TODO FIX

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
        

    def __createCMakeFileOnDemand(self, cmakeFileDat :CMakeData, shouldOverwrite :bool, file : str, content :str ):
        if os.path.exists(cmakeFileDat.getRelativeCMakeFilePath(file)) and not shouldOverwrite:
            print(f"Target File ({cmakeFileDat.getRelativeCMakeFilePath(file)}) Already exists")
        else: 
            with open(cmakeFileDat.getRelativeCMakeFilePath(file), "w") as file:                        
                file.write(content)    

    def __placeholderAsBackup(self, widget, placeholder:str):
        if(widget.text() == ""):
            widget.setText(placeholder)