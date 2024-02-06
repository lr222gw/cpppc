 
from logging import warn, warning
from os import path
import os
import re
import subprocess
import platform
import shutil
from src.dev.Terminate import WarnUser, terminate

def __isCompressedFile(path:str)->bool:
    return False #TODO: Implement this!


#TODO: This might not be necessary anymore, Might be able to remove it as it contains a lot of linux specific solutions...

def fetchLocalLib(libPath:str, libname:str,userProvidedLocalLibsPath:str,targetPath:str = "."):
    
    if len(libPath) == 0: 
        print(f"Can't fetch if path doesn't exist")
        exit()

    #Handle cases for copy and Install 
        
    # Determine if path is in userspace... 
    
    # Only copy if dir is inside user provided 'Local Libs' directory...
        
    abs_userProvidedLocalLibsPath   = path.abspath(userProvidedLocalLibsPath)
    if not path.isdir(abs_userProvidedLocalLibsPath): 
        terminate("User provided path is not a directory")        


    if path.isdir(libPath): 
        
        abs_LibPath   = path.abspath(libPath)

        # Check that library is within the provided path
        if path.commonpath([abs_userProvidedLocalLibsPath, abs_LibPath]) == abs_userProvidedLocalLibsPath:
            print(f"Library [{libPath}] \n\texists in users local libs at: {abs_LibPath}")
            shutil.copytree(abs_LibPath,os.path.join(targetPath,libname),dirs_exist_ok=True)
    else:

        # Check if name exists in users provided path
        libPathInUserLocalLibs = os.path.join(abs_userProvidedLocalLibsPath,libPath)
        if(path.isdir(libPathInUserLocalLibs)):
            print(f"Library [{libPath}] \n\texists in users local libs at: {libPathInUserLocalLibs}")
            shutil.copytree(libPathInUserLocalLibs,os.path.join(targetPath,libname),dirs_exist_ok=True)

        elif(__isCompressedFile(libPath)):
            # TODO: extract files ... 
            pass 

        else:
            # Might be installed
            pass  
                            

def getInstalledLib(libPath:str)->list[str]:
    reqLibs :list[str] = list[str]()
    if platform.system() == 'Linux':
        # if name, then check if it exists with ldconfig (LINUX!)
        # Also Check if ldconfig exists, and warn the user that it is required for this feature... 
        if shutil.which("pkg-config"):
            allLibs = subprocess.run(["pkg-config","--list-all"], capture_output=True, text=True )
            reqLibs_regx = re.compile(fr"\S*{libPath}\S*\s+[^\n]+", re.MULTILINE| re.IGNORECASE)
            decodedAllLibsStr = bytes(allLibs.__str__(),"utf-8").decode("unicode_escape")
            reqLibs = [lib.split(" ")[0] for lib in re.findall(reqLibs_regx, decodedAllLibsStr)]
            print(reqLibs)
        else: 
            WarnUser("pkg-config is not installed or missing from PATH, can't check if library is installed")            

            if not shutil.which("ldconfig"):
                WarnUser("ldconfig is not installed or missing from PATH, can't check if library is installed")
                # return  #? 
            else :
                allLibs = subprocess.run(["ldconfig","-p"], capture_output=True, text=True )
                reqLibs_regx = re.compile(fr"\S*{libPath}\S*\s+\([^)]+\)\s+=>", re.MULTILINE| re.IGNORECASE)
                decodedAllLibsStr = bytes(allLibs.__str__(),"utf-8").decode("unicode_escape")
                reqLibs = [lib.split(" ")[0] for lib in re.findall(reqLibs_regx, decodedAllLibsStr)]
                print(reqLibs)


        # subprocess.run()

        pass
    elif platform.system() == 'Windows':
        pass
    elif platform.system() == 'Darwin':
        pass
    
    return reqLibs

    