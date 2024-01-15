from os import path
import os
import subprocess
import re
from typing import Optional
from src.dev.Terminate import terminate
from .structs.CMakeVersionData import CMakeVersionData as CMakeVersionData
from PyQt5.QtWidgets import QSpinBox


def __checkInstalled_cmake():
    try: 
        versionstring = subprocess.run(['cmake', '--version'], capture_output=True, text=True )    
        
        return versionstring 
    except :
        print("Error:", "CMake is not installed")
        return False

def getCMakeVersion():
    res = __checkInstalled_cmake()
    if(res != False):        

        versions_regx = r"cmake version ([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})"
        match = re.match(versions_regx, str(res.stdout))
        
        if(match):
           major, minor, patch = match.groups()           
           return CMakeVersionData(int(major),int(minor),int(patch))
        else:
            print("Output from `cmake --version` have unexpected format.")            
            return CMakeVersionData()
    
    return CMakeVersionData()


#TODO: Remove graphviz part, cannot get anything out of parsing it
def configureCmakeProjectWithGraphviz(projectPath:str):
    try: 
        os.mkdir(projectPath+"/temp_cmake_configuration")
        absProjectPath = path.abspath(projectPath)
        output = subprocess.run(['cmake', '--graphviz=temp_cmake_configuration/p.dot'],cwd=absProjectPath, capture_output=True, text=True )    
        print(f"CMake configuration completed: {projectPath}")
        
    except :
        print("Error:", "CMake is not installed")
        return False
    

def getLibraryTargetFromPCFile(pcFilePath:str) -> Optional[str]:
    try:
        with open(pcFilePath, "r") as pcFile:
            libTarget =  [re.findall(r"-l(\S*)",line) for line in pcFile if 'Libs' in line]
            if  len(libTarget) > 1: 
                terminate("Unhandled exception, did not know there could be two libs in this line")        

            return libTarget[0][0] if len(libTarget) > 0 else None
        
    except :
        terminate(f"Error: Could not open file at {pcFilePath}!")
        return ""        