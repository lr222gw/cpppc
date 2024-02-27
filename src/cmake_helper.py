from os import path
import os
import subprocess
import re
from typing import Optional
from src.action_funcs import warningPopup
from src.dev.Terminate import terminate
from src.structs.PersistantDataManager import PersistantDataManager
from .structs.CMakeVersionData import CMakeVersionData as CMakeVersionData
from PyQt5.QtWidgets import QSpinBox

DIR_CMAKE_DEPENDENCY_CPPPC_DATA = ".cpppc_temp_build_dir"
FILE_CPPPC_DEPENDENT_DATA = "cpppc_data.cfg"

def __checkInstalled_cmake():
    try: 
        versionstring = subprocess.run(['cmake', '--version'], capture_output=True, text=True )    
        
        return versionstring 
    except :
        warningPopup("CMake is not installed")
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


def configureCmakeProjectDependency(projectPath:str) -> Optional[str]: # TODO: Consider Deprecate, not used anymore. Might reuse some cache ideas...
    configPath = path.join(projectPath, DIR_CMAKE_DEPENDENCY_CPPPC_DATA)
    configFilePath = path.join(projectPath, DIR_CMAKE_DEPENDENCY_CPPPC_DATA, FILE_CPPPC_DEPENDENT_DATA)
    try:     
        absProjectPath = path.abspath(projectPath)
        if not PersistantDataManager().checkDependencyExist(absProjectPath):
            #TODO: CheckHistory...            
            if not path.exists(configPath): 
                os.mkdir(configPath)
            output = subprocess.run(['cmake', f'--fresh {DIR_CMAKE_DEPENDENCY_CPPPC_DATA}'],cwd=absProjectPath, capture_output=True, text=True )    

        print(f"CMake configuration completed: {projectPath}")
        
    except :
        print("Error:", "Could not configure dependency CMake project")
        return None
    
    return configPath
    

def getLibraryTargetFromPCFile(pcFilePath:str) -> Optional[str]: #Not used anymore, Consider deprecate
    try:
        with open(pcFilePath, "r") as pcFile:
            libTarget =  [re.findall(r"-l(\S*)",line) for line in pcFile if 'Libs' in line]
            if  len(libTarget) > 1: 
                terminate("Unhandled exception, did not know there could be two libs in this line")        

            return libTarget[0][0] if len(libTarget) > 0 else None
        
    except :
        terminate(f"Error: Could not open file at {pcFilePath}!")
        return ""        