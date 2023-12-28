from .structs import GuiData as d
from .structs.ProjectConfigurationData import ProjectConfigurationData
from . import cmake_helper as hlp_cmake
from PyQt5.QtWidgets import QMessageBox, QTextEdit
import os
from . import cmake_helper as cm_hlp


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
    
    targetPath      = projdata.getTargetPath()
    targetSrcPath   = targetPath+"/src"
    targetCmakePath = targetPath+"/cmake"
    if os.path.exists(targetPath) and not projdata.get_overwriteProjectTargetDir():
        print("Target Already exists")
        return
    else:
        print("Target Will be Created")
        os.makedirs(targetPath, exist_ok=True)
        os.makedirs(targetSrcPath, exist_ok=True)
        os.makedirs(targetCmakePath, exist_ok=True)
        content=\
            genStr_cmake_min_version(projdata) +\
            genStr_cmake_projectdetails(projdata)

        # TODO: Add the sources... 

        if(projdata.get_useProgram_ccache()):
            content += cm_hlp.addCMakeCompilerLauncher("ccache")
            
        with open(targetPath+"/"+"CMakeLists.txt", "w") as file:                        
            file.write(content)
    

def genStr_cmake_min_version(projdata : ProjectConfigurationData) -> str:
    return f'''\
cmake_minimum_required(VERSION {projdata.cmakeVersionData.get_major()}.{projdata.cmakeVersionData.get_minor()}.{projdata.cmakeVersionData.get_patch()})\n    
'''

def genStr_cmake_projectdetails(projdata : ProjectConfigurationData)->str:    
    return f'''\
project(            
    {projdata.projectName_str()} 
    VERSON 0.0.1 
    DESCRIPTION \"{projdata.projectDesc_str()}\"
    LANGUAGES CXX C)
'''

def __placeholderAsBackup(widget, placeholder:str):
    if(widget.text() == ""):
        widget.setText(placeholder)