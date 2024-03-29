from enum import StrEnum
from genericpath import exists
import os
from pathlib import Path
import pathlib
import re
import shutil
import subprocess
from typing import Optional

from src.dev.Terminate import WarnUser, terminate
from src.structs.PersistantDataManager import TargetDatas, getCpppcDir, hash_directory, listDirectory, removeUnmatchingFilesInDir
from .CMakeParsingHelpers import *

def __derefernce(dict, var):
    variableReferencesName_regx = re.compile(r"\$\{([^}{]+)\}",re.IGNORECASE|re.MULTILINE)
    
    matched = re.findall(variableReferencesName_regx, var)

    # TODO: Fix redundant ifstatement in first return...
    if len(matched) > 0:        
        return dict[matched[0]] if matched[0] in dict else var
    else: 
        return var

def getLibraryTargets(libPath:str): # TODO: Unused, consider deprecate
    
    cmakevars = __getCMakeVarDefinitions(os.path.join(libPath,"CMakeLists.txt"))
    targets = list[str]()
    contents :str 
    with open(os.path.join(libPath,"CMakeLists.txt"), 'r') as file:
        contents = file.read()

    add_library_rgx = re.compile(r"add_library\((?:(?:[\S\-_]+|[\S\-_]+::[\S\-_]+)\s{1,}(?:ALIAS)\s+(\S+)|(?:([\S\-_]+|[\S\-_]+::[\S\-_]+)\s{0,}))(SHARED|STATIC|MODULE|INTERFACE|OBJECT){0,1}(?:.*)\)", re.IGNORECASE | re.MULTILINE)        
    matches = re.findall(add_library_rgx, contents)
    
    for match in matches :
        if match[0] != "":
            targets.append(__derefernce(cmakevars,match[0]))
        elif match[1] != "": 
            targets.append(__derefernce(cmakevars,match[1]))

    # Remove duplicates
    targets_cleaned = []
    for m in targets: 
        if not m in targets_cleaned:
            targets_cleaned.append(m)

    return targets_cleaned


def __existsInDictionary(m,p, skipPossibleTargets:Optional[bool] = False):            
    if p in m["PossibleTargets"] and not skipPossibleTargets :
        return True
    if p in m["SHARED"]:  
        return True
    if p in m["STATIC"]:  
        return True
    if p in m["INTERFACE"]:  
        return True
    
    return False
    
def __getLibraryTargets_cmakefile(cmakef:str) -> dict[str,list[str]]: #TODO: Rename function if it will do more than fetching targets...
    
    cmakevars = __getCMakeVarDefinitions(cmakef)

    basename = os.path.basename(cmakef)

    with open(cmakef, 'r') as file:
        add_library_rgx = re.compile(r"add_library\((?:(?:[\S\-_]+|[\S\-_]+::[\S\-_]+)\s{1,}(?:ALIAS)\s+(\S+)|(?:([\S\-_]+|[\S\-_]+::[\S\-_]+)\s{0,}))(SHARED|STATIC|MODULE|INTERFACE|OBJECT){0,1}(?:.*)\)", re.IGNORECASE | re.MULTILINE)
        possibleTargets_rgx = re.compile(r"(?:(?!(?:\w|\s)*[#\n])^.+(?:\bTARGET\s+([^\s\\)]+)))", re.IGNORECASE | re.MULTILINE)
        contents = file.read()
        
        matches = re.findall(add_library_rgx, contents)
        possibleTargetMatches = re.findall(possibleTargets_rgx, contents)
        
        includeMatches = re.findall(r"(?m)((?!(?:\w|\s)*[#\n]).*(?:target_include_directories)\(([^\s]+))", contents)

        m = dict[str,list[str]]()
        m["PossibleTargets"] = list[str]()        
        m["SHARED"] = list[str]()
        m["STATIC"] = list[str]()
        m["INTERFACE"] = list[str]()
        m["Includes"] = list[str]()
        m["ParsedComponentTargets"] = list[str]()

        temp_incl = [i[1] for i in includeMatches if len(i) == 2 ]        
        for i in temp_incl: 
            if not i in m["Includes"]:
                m["Includes"].append(i)
        
        
        for match in matches :
            if match[0] != "":
               if not match[1] in m:
                    m.setdefault(match[1],list[str]())
               m[match[1]].append(__derefernce(cmakevars,match[0]))
            elif match[1] != "" and match[2] != "": 
                if not match[2] in m:
                    m.setdefault(match[2],list[str]())
                m[match[2]].append(__derefernce(cmakevars,match[1]))
            elif match[1] != "" and match[0] == "" and match[2] == "":                
                m["STATIC"].append(__derefernce(cmakevars,match[1]))

        for p in possibleTargetMatches: 
            # If its a reference, add it only if we can get its value        
            if p[0] == "$" or p[0:2] == "\"$":
                derefenced = __derefernce(cmakevars,p)
                if derefenced != p:
                    m["PossibleTargets"].append(derefenced)
                    if "Targets-" in basename != -1:
                        m["ParsedComponentTargets"].append(derefenced)
            else : 
                m["PossibleTargets"].append(p)
                if "Targets-" in basename != -1 or "targets-" in basename != -1:
                        m["ParsedComponentTargets"].append(p)

        return m 

def __getCMakeVarDefinitions(CMakeFilePath:str ) -> dict[str,str]:
    CMakeVarDict :dict[str,str] = dict[str,str]()
    CMakeContents = ""
    with open(CMakeFilePath, 'r') as file:
        CMakeContents = file.read()

    # # 1. Collect all the calls to set
    set_calls_all_regx = re.compile(r"(?:\S*)set\((\s*(?:([^\s\")]+)\s+)((?:\"[^\"\n]+\"|[^\")\n]+)+)+(?:\s*))", re.IGNORECASE|re.MULTILINE)
    cvar_PROJECT_NAME_regx = re.compile(r"(?<!#)project\((?:\s*)([^ ]+)[^)]*\)",re.IGNORECASE|re.MULTILINE)

    # TODO:  Add more common CMake variables, such as ${PROJECT_NAME}
    # Set default values 
    project_name_match = re.findall(cvar_PROJECT_NAME_regx, CMakeContents)
    if len(project_name_match) != 0:
        CMakeVarDict["PROJECT_NAME"] =  project_name_match[0] if len(project_name_match) <= 1 else exit("Cannot be more than one project definition in one cmake file...") #terminate
    
    variableReferences_regx = re.compile(r"\$\{[^}{]+\}",re.IGNORECASE|re.MULTILINE)
    variableReferencesName_regx = re.compile(r"\$\{([^}{]+)\}",re.IGNORECASE|re.MULTILINE)
    allRefs = list(dict.fromkeys(re.findall(variableReferences_regx, CMakeContents)))

    # Initial set of all variables 
    all_set_calls = re.findall(set_calls_all_regx, CMakeContents)
    for match in all_set_calls:
         CMakeVarDict[match[1]] = match[2]
        

    #Clean up variables 
    cmakeVarDict_noRefs :dict[str,str] = dict[str,str]()
    for (var, val) in CMakeVarDict.items(): 
        
        allRefs = list(dict.fromkeys(re.findall(variableReferencesName_regx, val)))

        # dereference variable if it exists in dictionary, else use reference
        if(len(allRefs) > 0):
             for ref in allRefs: 
                pn = ""
                if len(project_name_match) != 0:
                    pn = CMakeVarDict["PROJECT_NAME"]
                if ref in CMakeVarDict:
                    cmakeVarDict_noRefs[ref] = CMakeVarDict[ref]
                elif isVarProvidedByCMake(ref, pn):
                    print(f"Variable not found in dict (Likely provided by CMake): {ref}")
                else :
                    # TODO: Consider if we need to terminate or not, probably not...
                    pass
                    # terminate(f"Variable not found!: {ref}")
                    
        else: 
             cmakeVarDict_noRefs[var] = val

    # Use value in dictionary for variable references
    def replacementString(match)->str:
        if match[1] in cmakeVarDict_noRefs:
            return cmakeVarDict_noRefs[match[1]]
        return match[0] #if match was not found, keep the variable refence...
            

    set_calls_strlist_regx = re.compile(r"((?:\s?(?:(?:(?:\"[^\"\n]*\")\s?){2,}))(?:PARENT_SCOPE|FORCE)?)", re.IGNORECASE|re.MULTILINE)
    
    # Finally, creating a correct dictionary
    cmakeVarDict_corrected :dict[str,str] = dict[str,str]()
    for (var, val) in CMakeVarDict.items(): 
        
        cmakeVarDict_corrected[var] = re.sub(variableReferencesName_regx, replacementString ,val)

        fixlist_match = re.findall(set_calls_strlist_regx, cmakeVarDict_corrected[var])
        for match in fixlist_match:
            cmakeVarDict_corrected[var] = ";".join(match.replace("\"","").split(" "))
        
        # TODO: handle cases where CMakeLists.txt creator uses one set to set multiple vars...
           
    return cmakeVarDict_corrected

def textnormalizer(text:str, toUpper:Optional[bool]=True, replaceNewl:Optional[bool]=True, replaceDoubleSpaces:Optional[bool]=True, ):
    def uppcasetext(part):
        if part.group(1): 
            return part.group(1)
        else:
            return part.group(0).upper()

    decodedOutput = text.encode().decode('unicode-escape')
    
    newlines_regx       = re.compile(r"\s*\n\s*", re.MULTILINE)
    doublespaces_regx   = re.compile(r"\s{2,}", re.MULTILINE)
    toupper_regx        = re.compile(r"(\"([^\"]*)\")|([^\"]+)", re.MULTILINE)
    strippedOutput = re.sub(newlines_regx,' ',decodedOutput)         if replaceNewl else decodedOutput
    strippedOutput = re.sub(toupper_regx,uppcasetext,strippedOutput) if toUpper else strippedOutput
    strippedOutput = re.sub(doublespaces_regx,' ',strippedOutput)    if replaceDoubleSpaces else strippedOutput
    return strippedOutput


class CmakeFindType(StrEnum):
    undef   = "undef"
    Package = "Package"
    Module  = "Module"

def _writelibdat(file, name):
    file.write(str.format("message(\"-- {}_FOUND:${{{}_FOUND}}\")\n",name,name))
    file.write(str.format("message(\"-- {}_ROOT:${{{}_ROOT}}\")\n",name,name))
    file.write(str.format("message(\"-- {}_DIR:${{{}_DIR}}\")\n",name,name))
    file.write(str.format("message(\"-- {}_LIBRARIES:${{{}_LIBRARIES}}\")\n",name,name))
    file.write(str.format("message(\"-- {}_LINK_LIBRARIES:${{{}_LINK_LIBRARIES}}\")\n",name,name))
    file.write(str.format("message(\"-- {}_LIBRARY_DIRS:${{{}_LIBRARY_DIRS}}\")\n",name,name))
    file.write(str.format("message(\"-- {}_LDFLAGS:${{{}_LDFLAGS}}\")\n",name,name))
    file.write(str.format("message(\"-- {}_LDFLAGS_OTHER:${{{}_LDFLAGS_OTHER}}\")\n",name,name))
    file.write(str.format("message(\"-- {}_INCLUDE_DIRS:${{{}_INCLUDE_DIRS}}\")\n",name,name))
    file.write(str.format("message(\"-- {}_CFLAGS:${{{}_CFLAGS}}\")\n",name,name))
    file.write(str.format("message(\"-- {}_CFLAGS_OTHER:${{{}_CFLAGS_OTHER}}\")\n",name,name))
    file.write(str.format("message(\"-- {}_INCLUDEDIR:${{{}_INCLUDEDIR}}\")\n",name,name))
    file.write(str.format("message(\"-- {}_INCLUDE_DIR:${{{}_INCLUDE_DIR}}\")\n",name,name))
    file.write(str.format("message(\"-- {}_LIBDIR:${{{}_LIBDIR}}\")\n",name,name))

def __getFinderCmakeOutput_installed(name:str):
    finderCMakeFile = Path.joinpath(getCpppcDir(), "CMakeLists.txt")
    finder_tempPath = Path.joinpath(getCpppcDir(), "temp")
    Path.touch(finderCMakeFile)
    # TODO: Consider using CMakeFindDependencyMacro in order to use find_dependency to find more dependables...
    with finderCMakeFile.open("w") as file:
        file.write(f"cmake_minimum_required(VERSION 3.28.0)\n")
        file.write("project(find_dummy)\n")
        file.write(f"find_package({name} )\n") # TODO: Consider f"find_package({name} NAMES {name.upper()} {name.lower()})\n"
        file.write(f"if(NOT ${{{name}_FOUND}})\n")
        file.write(f"\tfind_package({name.upper()})\n")
        file.write(f"\tif(NOT ${{{name.upper()}_FOUND}})\n")
        file.write(f"\t\tfind_package({name.lower()})\n")
        file.write(f"\t\tif(NOT ${{{name.lower()}_FOUND}})\n")
        file.write(f"\t\t\tmessage(FATAL_ERROR \"Could Not find Library '{name}'\")\n")
        file.write(f"\t\tendif()\n")
        file.write(f"\tendif()\n")
        file.write(f"endif()\n")
        file.write(f"message(\"###LibraryData###\")\n")
        
        _writelibdat(file,name)
        _writelibdat(file,name.upper())
        _writelibdat(file,name.lower())

        file.write(str.format("get_cmake_property(_variableNames VARIABLES)\n"))
        file.write(str.format("foreach(_variableName ${{_variableNames}})\n"))
        file.write(str.format("message(STATUS \"${{_variableName}} = ${{${{_variableName}}}}\")\n"))
        file.write(str.format("endforeach()\n"))
    
    output = subprocess.run(["cmake", "--debug-find", f"{finderCMakeFile.absolute().__str__()}", f"-B {finder_tempPath.absolute().__str__()}"] ,text=True, capture_output=True)
    
    shutil.rmtree(finder_tempPath.absolute().__str__())
    return output
 
def __getFinderCmakeOutput_local(name:str, includeFiles:list[str]): #TODO: Consider if we need this... Might be worth it for some libraries! S
    finderCMakeFile    = Path.joinpath(getCpppcDir(), "CMakeLists.txt")
    finder_tempPath    = Path.joinpath(getCpppcDir(), "temp")
    finder_libTempPath = Path.joinpath(finder_tempPath, "templib")
    includes=""
    theConf = ""
    theConfPath = ""
    for f in includeFiles:
        basename = os.path.basename(f)
        r = basename.find("Config.cmake")
        if r != -1:
            theConf = basename[0:r]
            theConfPath = f.split(theConf)[0]

    for file in includeFiles:
        # includes += f"include({os.path.join(includeFiles,file)})\n"
        includes += f"include({file})\n"
    Path.touch(finderCMakeFile)
    with finderCMakeFile.open("w") as file:
        file.write(f"cmake_minimum_required(VERSION 3.28.0)\n") #TODO: Not hardcode version... fetch users instead
        file.write("project(find_dummy)\n")
        file.write(f"find_package({theConf} PATHS {theConfPath} NO_DEFAULT_PATH)") #TODO: Make sure this works, might need to include isntead, as before
        file.write(f"message(\"###LibraryData###\")\n")
        
        _writelibdat(file,name)
        _writelibdat(file,name.upper())
        _writelibdat(file,name.lower())

        file.write(str.format("get_cmake_property(_variableNames VARIABLES)\n"))
        file.write(str.format("foreach(_variableName ${{_variableNames}})\n"))
        file.write(str.format("message(STATUS \"${{_variableName}} = ${{${{_variableName}}}}\")\n"))
        file.write(str.format("endforeach()\n"))
    
    # shutil.copytree(os.path.abspath(includeFiles),finder_libTempPath.absolute().__str__())
    pathlib.Path(finder_libTempPath.absolute().__str__()).mkdir(exist_ok=True, parents=True)
    for f in includeFiles:
        shutil.copyfile(f,os.path.join(finder_libTempPath.absolute().__str__(),os.path.basename(f)))

    output = subprocess.run(["cmake", "--debug-find", f"{finderCMakeFile.absolute().__str__()}", f"-B {finder_tempPath.absolute().__str__()}"] ,text=True, capture_output=True)
    
    shutil.rmtree(finder_tempPath.absolute().__str__())
    return output 

def __getCmakeConfPath(name:str,output:subprocess.CompletedProcess[str],printdbg:Optional[bool]=False) -> tuple[Optional[str], CmakeFindType, dict[str,str], str]: 
    
    if printdbg:
        print(output.__str__().encode("utf-8").decode('unicode-escape'))
    
    strippedOutput = textnormalizer(output.__str__(), toUpper=False, replaceNewl=False)

    path_pkg_regx = re.compile(fr"The file was found at\s+([\w \/():.-]+(?:\\|/)({name})(?:-[0-9.]+)?(?:\\|/)[\w \\()/.-]+)", re.IGNORECASE | re.MULTILINE)
    path_module_regx = re.compile(fr"The file was found at\s+([\w \\()/:.-]+(?:\\|/)Modules(?:\\|/)Find([\w\\()/.-]+)+?\.cmake)", re.IGNORECASE | re.MULTILINE)

    messagedata_regx = re.compile(fr"-- ({name}_[^=:\n]+?)(?::|=\s)(?!\n)([^\n]+?)\n", re.IGNORECASE | re.MULTILINE)
    msgDatDict = dict[str,str]()    

    messageData = re.findall(messagedata_regx,str(output.stderr + output.stdout))
    for m in messageData:
        msgDatDict[m[0]] = m[1]
    
    pathMatch = re.findall(path_pkg_regx,str(output.stderr + output.stdout))
    if pathMatch != None and len(pathMatch) > 0:
        return (pathMatch[0][0], CmakeFindType.Package, msgDatDict,pathMatch[0][1])
    
    pathMatch = re.findall(path_module_regx,str(output.stderr + output.stdout))
    if pathMatch != None and len(pathMatch) > 0:
        return (pathMatch[0][0], CmakeFindType.Module, msgDatDict, pathMatch[0][1])

    return (None,CmakeFindType.undef, msgDatDict, name)

def collectGeneratedConfigs(libPath,printdbg:Optional[bool]=False): 
        
    finder_tempPath    = Path.joinpath(getCpppcDir(), "temp")
    finder_libparse    = Path.joinpath(getCpppcDir(), "libparse")

    libPath = Path(libPath)

    # Save Original directory file listing in case changed
    hashbefore_cmake = hash_directory(libPath.absolute().__str__())
    fileListingBefore_cmake = listDirectory(libPath.absolute().__str__())
    
    # Run command to generate possible config files...
    output = subprocess.run(["cmake", "--fresh",f"-S {libPath.absolute().__str__()}", f"-B {finder_tempPath.absolute().__str__()}"] ,text=True, capture_output=True)
    
    # Remove Any files added from running cmake command
    if(hashbefore_cmake != hash_directory(libPath.absolute().__str__())):
        fileListingAfter_cmake = listDirectory(libPath.absolute().__str__())
        removeUnmatchingFilesInDir(fileListingBefore_cmake,fileListingAfter_cmake)

    if printdbg:
        print(output.__str__().encode("utf-8").decode('unicode-escape'))
    
    exports = finder_tempPath / "CMakeFiles" / "Export"
    allExports :list[Path] = []
    if exports.exists():
        allExports = [file for dir in exports.iterdir() if dir.is_dir() for file in dir.iterdir()]
    confs = [f for f in finder_tempPath.glob("*.cmake")]
    if len(confs) > 0: 
        allExports.extend(confs)
    libCmakeText = libPath / "CMakeLists.txt"
    if libCmakeText.exists(): 
        allExports.append(libCmakeText)

    if finder_libparse.exists():
        shutil.rmtree(finder_libparse.absolute().__str__())
    finder_libparse.mkdir(parents=True,exist_ok=True)
    movedExports:list[str] =[]
    for f in allExports:
        shutil.copyfile(f,os.path.join(finder_libparse.absolute().__str__(),f.name))
        movedExports.append(os.path.join(finder_libparse.absolute().__str__(),f.name))

    shutil.rmtree(finder_tempPath.absolute().__str__())

    return movedExports


def collectFilePaths(filesToInclude: list[str], dirsToCollectFrom: list[str])->list[str]:
    """
    Adds all files to a single list
    """
    allFiles = list[str]()
    allFiles = [os.path.abspath(f) for f in filesToInclude]
    for dir in dirsToCollectFrom:
        if os.path.exists(dir):
            for f in os.listdir(dir):
                allFiles.append(os.path.join(dir,f))
        else:
            WarnUser(f"Path not found: {dir}")

    allFiles = [f for f in allFiles if os.path.isfile(os.path.abspath(f))]

    return allFiles

def gatherTargetsFromConfigFiles(configFiles:list[str], workpath:str)->TargetDatas:
    pathlib.Path(workpath).mkdir(exist_ok=True)
    # targets = []
    targets = dict[str,list[str]]()
    targetFiles = list[str]()
    findFiles = list[str]()
    
    for file in configFiles: 
        if os.path.isfile(file):        
            shutil.copyfile(file, os.path.join(workpath, os.path.basename(file)))
            targetFiles.append(os.path.join(workpath, os.path.basename(file)))
            
    for targetfile in targetFiles:    
        t = __getLibraryTargets_cmakefile(targetfile)
        for fileTargetsKey, fileTargetsVal  in t.items(): 
            if not fileTargetsKey in targets:
                targets.setdefault(fileTargetsKey,list[str]())
            targets[fileTargetsKey].extend(fileTargetsVal)

    #Remove entries from PossibleTargets if known type
    targets["PossibleTargets"] = [t for t in targets["PossibleTargets"] if not __existsInDictionary(targets,t,skipPossibleTargets=True)]

    # Remove duplicates
    targets_cleaned:dict[str,list[str]] = dict()
    targets_cleaned.setdefault("PossibleTargets", list[str]())
    targets_cleaned.setdefault("SHARED", list[str]())
    targets_cleaned.setdefault("STATIC", list[str]())
    targets_cleaned.setdefault("INTERFACE", list[str]())
    targets_cleaned.setdefault("Includes", list[str]())
    targets_cleaned.setdefault("ParsedComponentTargets", list[str]())
    for k, v in targets.items(): 
        if k in ["PossibleTargets", "SHARED", "STATIC", "INTERFACE", "Includes", "ParsedComponentTargets"]:
            for vv in targets[k]:
                if not vv in targets_cleaned[k]:
                    targets_cleaned[k].append(vv)

    return TargetDatas(
        targets_cleaned["PossibleTargets"], 
        targets_cleaned["SHARED"], 
        targets_cleaned["STATIC"], 
        targets_cleaned["INTERFACE"], 
        targets_cleaned["ParsedComponentTargets"],
        includes=targets_cleaned["Includes"])


def __printResults(targets : TargetDatas):
        
    if targets != None:
        if targets.keyWords != None:
            print(f"KeyWords:")
            for k, v in targets.keyWords.items(): 
                print(str.format("\t{}: {}",k,v))

        if(len(targets.possibleTargets) > 0):
            print(f"\nPossibleTargets:")
            for i in targets.possibleTargets: 
                print(str.format("\t{}",i))
        if(len(targets.STATIC) > 0):
            print(f"\nSTATIC:")
            for i in targets.STATIC: 
                print(str.format("\t{}",i))                
        if(len(targets.SHARED) > 0):
            print(f"\nSHARED:")
            for i in targets.SHARED: 
                print(str.format("\t{}",i))
        if(len(targets.INTERFACE) > 0):
            print(f"\nINTERFACE:")
            for i in targets.INTERFACE:
                print(str.format("\t{}",i))
    

def parseLib(name : str, confFilePaths: Optional[list[str]] = None) -> TargetDatas: 
    foundLib=True

    output:subprocess.CompletedProcess[str]
    if confFilePaths == None:
        output = __getFinderCmakeOutput_installed(name)
    else:
        output = __getFinderCmakeOutput_local(name, confFilePaths)

    p = __getCmakeConfPath(name, output)
    thePath = p[0]
    cmaketype= p[1]
    msgDatDict = p[2]
    name = p[3]

    targets : TargetDatas = TargetDatas([],[],[],[])
    if(thePath != None):
                
        if (cmaketype == CmakeFindType.Package):
            print(f"Found \"{name}\" at : {thePath}")
            
            confFiles = collectFilePaths([],[os.path.abspath(os.path.join(thePath,os.pardir))])            
            finder_tempPath = Path.joinpath(getCpppcDir(), "temp_lib")
            targets = gatherTargetsFromConfigFiles(confFiles,finder_tempPath.absolute().__str__())
        elif cmaketype == CmakeFindType.Module:
            print(f"Found \"{name}\" at : {thePath}")
            finder_tempPath = Path.joinpath(getCpppcDir(), "temp_lib")
            confFiles = collectFilePaths([os.path.abspath(thePath)],[])
            targets = gatherTargetsFromConfigFiles(confFiles,finder_tempPath.absolute().__str__())

        targets.find_package = name

    else:
        print(f"Did not find \"{name}\"... ")
    
    
    targets.keyWords = msgDatDict
    __printResults(targets)    

    
    return targets
