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
           return CMakeVersionData(int(major),int(minor),int(patch))
        else:
            print("Output from `cmake --version` have unexpected format.")            
            return CMakeVersionData()
    
    return CMakeVersionData()
