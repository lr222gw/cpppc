from dataclasses import dataclass, field
from .CMakeDataHelper import *
from .CppDataHelper import *
from .ProjectConfigurationData import *
import os

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
        self.__generateCMakeLists()
        self.__generateCPPFiles()

    def decideOrder(self):
        self.cmakeListDat.appendOrder(CMC_cmake_minimum_required)
        self.cmakeListDat.appendOrder(CMC_project)
        self.cmakeListDat.appendOrder(CMC_include)
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
            os.makedirs(self.cmakeListDat.getPathInTarget(self.cmakeListDat.srcDirPath),    exist_ok=True)
            os.makedirs(self.cmakeListDat.getPathInTarget(self.cmakeListDat.cmakeDirPath),  exist_ok=True)

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
            
    def requireCMakeCppBridge(self):
        self.cmakeListDat.addToCMakeList(self.cmakeListDat.genStr_includeCmakeFile(self.cmakeListDat.FILE_cmake_cpp_data))
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
        

    def __createCMakeFileOnDemand(self, cmakeFileDat :CMakeDataHelper, shouldOverwrite :bool, file : str, content :str ):
        if os.path.exists(cmakeFileDat.getRelativeCMakeFilePath(file)) and not shouldOverwrite:
            print(f"Target File ({cmakeFileDat.getRelativeCMakeFilePath(file)}) Already exists")
        else: 
            with open(cmakeFileDat.getRelativeCMakeFilePath(file), "w") as file:                        
                file.write(content)    

    def createFileOnDemand(self, file : str, content :str, shouldOverwrite :bool = False):
        if os.path.exists(self.projDat.getPathInTarget(file)) and not shouldOverwrite:
            print(f"Target File ({self.projDat.getPathInTarget(file)}) Already exists")
        else: 
            with open(self.projDat.getPathInTarget(file), "w") as file:                        
                file.write(content)                

    def __placeholderAsBackup(self, widget, placeholder:str):
        if(widget.text() == ""):
            widget.setText(placeholder)