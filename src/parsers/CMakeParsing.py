import re

from src.dev.Terminate import terminate
from .CMakeParsingHelpers import *

#TODO: Refactory pathify from src.structs.CMakeDataHelper, avoid having 2...
def __pathify(*args :str) -> str:
        return "/".join(args)

def getLibraryTargets(libPath:str):
    
    cmakevars = __getCMakeVarDefinitions(__pathify(libPath,"CMakeLists.txt"))

    with open(__pathify(libPath,"CMakeLists.txt"), 'r') as file:
        add_library_rgx = re.compile(r"add_library\(([\S-]+|[\S-]+::[\S-]+)\s{0,}ALIAS (\S+){0,1}(SHARED|STATIC|MODULE){0,1}\s{0,}(\S*)\s{0,}\)", re.IGNORECASE | re.MULTILINE)
        contents = file.read()
        
        matches = re.findall(add_library_rgx, contents)
        
        return ["".join(__derefernce(cmakevars,match[1]) for match in matches if match[1] != "")]

def __derefernce(dict, var):
    variableReferencesName_regx = re.compile(r"\$\{([^}{]+)\}",re.IGNORECASE|re.MULTILINE)
    
    matched = re.findall(variableReferencesName_regx, var)

    # TODO: Fix redundant ifstatement in first return...
    if len(matched) > 0:        
        return dict[matched[0]] if matched[0] in dict else var
    else: 
        return var

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
    CMakeVarDict["PROJECT_NAME"] =  project_name_match[0] if len(project_name_match) == 1 else exit("Cannot be more than one project definition in one cmake file...") #terminate
    
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
                if ref in CMakeVarDict:
                    cmakeVarDict_noRefs[ref] = CMakeVarDict[ref]
                elif isVarProvidedByCMake(ref, CMakeVarDict["PROJECT_NAME"]):
                    print(f"Variable not found in dict (Likely provided by CMake): {ref}")
                else :
                    terminate(f"Variable not found!: {ref}")
                    
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
