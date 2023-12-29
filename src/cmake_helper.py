import subprocess
import re
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
        #    print(f"test {res.stdout} -> {major}.{minor}.{patch}")
           majorbox = QSpinBox()
           majorbox.setValue(int(major))
           minorbox = QSpinBox()
           minorbox.setValue(int(minor))
           patchbox = QSpinBox()
           patchbox.setValue(int(patch))
           cmakeVersonData = CMakeVersionData(majorbox,minorbox,patchbox)
           return cmakeVersonData
        else:
            print("Output from `cmake --version` have unexpected format.")
            cmakeVersonData = CMakeVersionData(0, 0, 0)
            return cmakeVersonData


#TODO: Move genStr to CmakeData class
def genStr_find_cmake_tool(tool:str, name:str, name_var:str) -> str:    

    content=f'''\
find_{tool}({name_var} {name})
'''
    return content

def addCMakeCompilerLauncher(programName : str) -> str:
    name_var=f"{programName}_program_var"
    content=f'''\
{genStr_find_cmake_tool("program", programName, name_var)}
if({name_var})
    set(CMAKE_CXX_COMPILER_LAUNCHER "${name_var}") # TODO: Do not override "CMAKE_*" variables, it could've been declare before or after this... hmm?
    #set(CMAKE_CUDA_COMPILER_LAUNCHER "${name_var}") # CMake 3.9+ Think about usingh this...
endif()'''
    return content
    