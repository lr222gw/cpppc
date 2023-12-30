from .structs import GuiData as d
from .structs.ProjectConfigurationData import ProjectConfigurationData
from . import cmake_helper as hlp_cmake
from PyQt5.QtWidgets import QMessageBox, QTextEdit
import os
from . import cmake_helper as cm_hlp
from .structs.CMakeData import *


# Testing access of input data
def test(guidata : d.GuiData):
    alert = QMessageBox(text= "User provided following input: "+guidata.widget.text() )
    alert.exec()

def cmakebuttontest():
    hlp_cmake.getCMakeVersion()

def createProject(projdata : ProjectConfigurationData):
    print("Creating Project")
    projdata.toString()
    __generateCMakeLists(projdata)


def __generateCMakeLists(projdata : ProjectConfigurationData):
    
    __placeholderAsBackup(projdata.projectTargetDir.widget, projdata.projectTargetDir.widget.placeholderText())    
    
    __placeholderAsBackup(projdata.projectName.widget, projdata.projectName.widget.placeholderText())    

    __placeholderAsBackup(projdata.projectExecName.widget, projdata.projectExecName.widget.placeholderText())
    
    cmakeDat = CMakeData()    
    cmakeDat.setTargetDirPaths(projdata.getTargetPath())
    cmakeDat.initCmakeVars(projdata)
    cmakeDat.initCmakeFuncs(projdata)
    
    if os.path.exists(projdata.getTargetPath()) and not projdata.overwriteProjectTargetDir.getState():
        print("Target Already exists")
        return
    else:
        print("Target Will be Created")
        os.makedirs(cmakeDat.targetDirPath, exist_ok=True)
        os.makedirs(cmakeDat.getPathInTarget(cmakeDat.srcDirPath),    exist_ok=True)
        os.makedirs(cmakeDat.getPathInTarget(cmakeDat.cmakeDirPath),  exist_ok=True)
        cmakeDat.addToCMakeList(cmakeDat.genStr_cmake_min_version(projdata))
        cmakeDat.addToCMakeList(cmakeDat.genStr_cmake_projectdetails(projdata))
        
        if(projdata.useProgram_ccache.getState()):
            cmakeDat.addToCMakeList(cm_hlp.addCMakeCompilerLauncher("ccache"))

        cmakeDat.addToCMakeList(cmakeDat.genStr_cmake_sourceDirVar())
        cmakeDat.addToCMakeList(cmakeDat.genStr_cmake_sources())
        cmakeDat.addToCMakeList(cmakeDat.genStr_cmake_headers())

        cmakeDat.addToCMakeList(cmakeDat.genStr_addExecutable(projdata))
        cmakeDat.addToCMakeList(cmakeDat.genStrHlp_addingProjectsTargetSources(projdata))

        if(projdata.useSanitizers.getState()):
            cmakeDat.addToCMakeList(cmakeDat.genStr_compileSanitizers(projdata))
            cmakeDat.addToCMakeList(cmakeDat.genStr_linkSanitizers(projdata))
        
        if(projdata.useMeasureCompiletime.getState()):
            cmakeDat.addToCMakeList(cmakeDat.genStr_compileTimeProperty(projdata))

        cmakeDat.addToCMakeList(cmakeDat.genStr_cppProperties(projdata))

        if(projdata.useCmakeCppBridge.getState()):     

            createCMakeFileOnDemand(
                cmakeDat, projdata.overwriteProjectTargetDir.getState(), 
                cmakeDat.FILE_cmake_cpp_data, 
                cmakeDat.genStr_FILE_cmake_cpp_data(projdata))

            createCMakeFileOnDemand(
                cmakeDat, projdata.overwriteProjectTargetDir.getState(), 
                cmakeDat.FILE_cmake_inputs_h_in, 
                cmakeDat.genStr_FILE_cmake_inputs_h_in(projdata))
            
        with open(cmakeDat.targetDirPath+"/"+"CMakeLists.txt", "w") as file:                        
            file.write(cmakeDat.getCMakeListStr())
    

def createCMakeFileOnDemand(cmakeDat :CMakeData, shouldOverwrite :bool, file : str, content :str ):
    if os.path.exists(cmakeDat.getRelativeCMakeFilePath(file)) and not shouldOverwrite:
        print(f"Target File ({cmakeDat.getRelativeCMakeFilePath(file)}) Already exists")
    else: 
        with open(cmakeDat.getRelativeCMakeFilePath(file), "w") as file:                        
            file.write(content)    

def __placeholderAsBackup(widget, placeholder:str):
    if(widget.text() == ""):
        widget.setText(placeholder)