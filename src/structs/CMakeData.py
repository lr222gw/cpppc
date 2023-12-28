import re
import textwrap
from .ProjectConfigurationData import ProjectConfigurationData
from dataclasses import dataclass, field

CMVAR__SOURCE_DIR : str   = "_SOURCE_DIR"
CMVAR__SOURCES    : str   = "_SOURCES"
CMVAR__HEADERS    : str   = "_HEADERS"

CMAKE_CURRENT_SOURCE_DIR = "${{CMAKE_CURRENT_SOURCE_DIR}}"

def CMAKIFY_PathToSourceDir(path:str) -> str:
    return str.format("{}",CMAKE_CURRENT_SOURCE_DIR+"/"+path)

@dataclass
class CMakeData : 
    # Directory Paths 
    targetDirPath   :str = "."
    srcDirPath      :str = "src"
    cmakeDirPath    :str = "cmake"
    def setTargetDirPaths(self, path :str):
        self.targetDirPath  = path
        self.srcDirPath     = "src"
        self.cmakeDirPath   = "cmake"
    
    def getPathInTarget(self, targetInsidePath : str) -> str:
        return self.targetDirPath + "/" + targetInsidePath

    def getSourcePaths(self) ->list:
        return {
            CMAKIFY_PathToSourceDir(self.srcDirPath)+"/*.cpp",
            CMAKIFY_PathToSourceDir(self.srcDirPath)+"/*.c",
            CMAKIFY_PathToSourceDir(self.srcDirPath)+"/*.hpp",
            CMAKIFY_PathToSourceDir(self.srcDirPath)+"/*.h",
        }
    
    def getHeaderPaths(self) ->list:
        return {
            CMAKIFY_PathToSourceDir(self.srcDirPath)+"/*.hpp",
            CMAKIFY_PathToSourceDir(self.srcDirPath)+"/*.h",
        }

    cmakeVars : dict = field(default_factory=dict)
    def initCmakeVars(self,projData : ProjectConfigurationData):        
        self.cmakeVars[CMVAR__SOURCE_DIR] = projData.projectName_str() + CMVAR__SOURCE_DIR
        self.cmakeVars[CMVAR__SOURCES]    = projData.projectName_str() + CMVAR__SOURCES
        self.cmakeVars[CMVAR__HEADERS]    = projData.projectName_str() + CMVAR__HEADERS

    def genStr_setVar(self, varName:str,varValue:str) -> str:
        return str.format("set({} {})", self.cmakeVars[varName], str.format(f"{varValue}"))

    def genStr_cmake_sources(self) -> str:     
        return f'''{self.genStr_setVar(CMVAR__SOURCE_DIR, CMAKIFY_PathToSourceDir(self.srcDirPath))}
    {self.genStr_file_globRecurse_ConfigureDepends(CMVAR__SOURCES,self.getSourcePaths())}
    {self.genStr_file_globRecurse_ConfigureDepends(CMVAR__HEADERS,self.getHeaderPaths())}\n'''

    def genStr_cmake_min_version(self, projdata : ProjectConfigurationData) -> str:
        return f'''cmake_minimum_required(VERSION {projdata.cmakeVersionData.get_major()}.{projdata.cmakeVersionData.get_minor()}.{projdata.cmakeVersionData.get_patch()})\n'''

    def genStr_cmake_projectdetails(self, projdata : ProjectConfigurationData)->str:    
        
        return textwrap.indent(
            re.sub(r'^[ \t]+', '', f'''project(            
            {projdata.projectName_str()} 
            VERSION 0.0.1
            DESCRIPTION \"{projdata.projectDesc_str()}\"
            LANGUAGES CXX C)\n\n''',0, re.MULTILINE),
            '\t'
        )[1:] #TODO: Let user set VERSION and LANGUAGES        
    def genStr_file_globRecurse_ConfigureDepends(self, varName : str, dirs :list) -> str:
        return str.format("\nFILE(GLOB_RECURSE {} CONFIGURE_DEPENDS\n    {}\n)", self.cmakeVars[varName], str.format("\n\t".join(dirs)) )