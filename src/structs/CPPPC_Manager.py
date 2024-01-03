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

    def createProject(self, projdata : ProjectConfigurationData):
        print("Creating Project")
        projdata.toString()
        self.__generateCMakeLists(projdata)


    def __generateCMakeLists(self, projdata : ProjectConfigurationData):
        
        __placeholderAsBackup(projdata.projectTargetDir.widget, projdata.projectTargetDir.widget.placeholderText())    
        
        __placeholderAsBackup(projdata.projectName.widget, projdata.projectName.widget.placeholderText())    

        __placeholderAsBackup(projdata.projectExecName.widget, projdata.projectExecName.widget.placeholderText())

        #TODO: Make placeholderAsBackup a behavior of a class rather than forced here...
        __placeholderAsBackup(projdata.entryPointFile.widget, projdata.entryPointFile.widget.placeholderText())
        
        cmakeListDat = CMakeData(projdata)

        cppDat = CppDataHelper(projdata, cmakeListDat)
        
        if os.path.exists(projdata.getTargetPath()) and not projdata.overwriteProjectTargetDir.getState():
            print("Target Already exists")
            return
        else:
            print("Target Will be Created")
            os.makedirs(cmakeListDat.targetDirPath, exist_ok=True)
            os.makedirs(cmakeListDat.getPathInTarget(cmakeListDat.srcDirPath),    exist_ok=True)
            os.makedirs(cmakeListDat.getPathInTarget(cmakeListDat.cmakeDirPath),  exist_ok=True)
            cmakeListDat.addToCMakeList(cmakeListDat.genStr_cmake_min_version(projdata))
            cmakeListDat.addToCMakeList(cmakeListDat.genStr_cmake_projectdetails(projdata))
            
            if(projdata.useProgram_ccache.getState()):
                cmakeListDat.addToCMakeList(cmakeListDat.addCMakeCompilerLauncher("ccache"))
                # cmakeDat.addToCMakeList(cm_hlp.addCMakeCompilerLauncher("ccache"))

            # if(projdata.useCmakeCppBridge.getState()): #TODO: FIX
            if(True): #TODO: FIX
                cmakeListDat.addToCMakeList(cmakeListDat.genStr_includeCmakeFile(cmakeListDat.FILE_cmake_cpp_data))

            cmakeListDat.addToCMakeList(cmakeListDat.genStr_cmake_sourceDirVar())
            cmakeListDat.addToCMakeList(cmakeListDat.genStr_cmake_sources())
            cmakeListDat.addToCMakeList(cmakeListDat.genStr_cmake_headers())

            cmakeListDat.addToCMakeList(cmakeListDat.genStr_addExecutable(projdata))
            cmakeListDat.addToCMakeList(cmakeListDat.genStrHlp_addingProjectsTargetSources(projdata))

            if(projdata.useSanitizers.getState()):
                cmakeListDat.addToCMakeList(cmakeListDat.genStr_compileSanitizers(projdata))
                cmakeListDat.addToCMakeList(cmakeListDat.genStr_linkSanitizers(projdata))
            
            if(projdata.useMeasureCompiletime.getState()):
                cmakeListDat.addToCMakeList(cmakeListDat.genStr_compileTimeProperty(projdata))

            cmakeListDat.addToCMakeList(cmakeListDat.genStr_cppProperties(projdata))

            #TODO: Only add this line if users checked use CMakeToCpp Bridge...
            cmakeListDat.addToCMakeList(cmakeListDat.genStr_callFunction(
                CMFUNC__add_cmake_inputs_to_targets, 
                [
                    projdata.projectExecName_str(),

                ])
            )

            cmakeListDat.addToCMakeList(cmakeListDat.genStr_targetLinkLibraries(projdata))
            

            # if(projdata.useCmakeCppBridge.getState()):     
            if(True): #TODO FIX
                cmake_inputs_fileDat = CMakeData(projdata)

                createCMakeFileOnDemand(
                    cmake_inputs_fileDat, projdata.overwriteProjectTargetDir.getState(), 
                    cmake_inputs_fileDat.FILE_cmake_cpp_data, 
                    cmake_inputs_fileDat.genStr_FILE_cmake_cpp_data(projdata))

                createCMakeFileOnDemand(
                    cmake_inputs_fileDat, projdata.overwriteProjectTargetDir.getState(), 
                    cmake_inputs_fileDat.FILE_cmake_inputs_h_in, 
                    cmake_inputs_fileDat.genStr_FILE_cmake_inputs_h_in(projdata))
                
            with open(cmakeListDat.targetDirPath+"/"+"CMakeLists_OLD.txt", "w") as file:                        
                file.write(cmakeListDat.getCMakeListStr())

            # New version
            with open(cmakeListDat.targetDirPath+"/"+"CMakeLists.txt", "w") as file:
                file.write(cmakeListDat.genCMakeList())

            #TODO: Move other file creation below creation of CMakeLists.txt 

            cppDat.createCppEntryPointFileOnDemand(cppDat.genStr_FILE_entrypoint())
        

def createCMakeFileOnDemand(cmakeFileDat :CMakeData, shouldOverwrite :bool, file : str, content :str ):
    if os.path.exists(cmakeFileDat.getRelativeCMakeFilePath(file)) and not shouldOverwrite:
        print(f"Target File ({cmakeFileDat.getRelativeCMakeFilePath(file)}) Already exists")
    else: 
        with open(cmakeFileDat.getRelativeCMakeFilePath(file), "w") as file:                        
            file.write(content)    

def __placeholderAsBackup(widget, placeholder:str):
    if(widget.text() == ""):
        widget.setText(placeholder)

