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
    cmakelist_str : str = "#CMakeLists.txt Generated through CPPPC\n"
    # Directory Paths 
    targetDirPath   :str = "."
    srcDirPath      :str = "src"
    cmakeDirPath    :str = "cmake"
    def setTargetDirPaths(self, path :str):
        self.targetDirPath  = path
        self.srcDirPath     = "src"
        self.cmakeDirPath   = "cmake"

    def addToCMakeList(self, string : str):
        self.cmakelist_str += string + "\n\n"

    def getCMakeListStr(self) -> str:
        return self.cmakelist_str
    
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

    # TODO: Support other than Clang!
    def genStr_setTargetCompileOptions(self, projData: ProjectConfigurationData,options:list) -> str:
        return str.format("target_compile_options({} PRIVATE $<$<CXX_COMPILER_ID:Clang>: {} > )", 
            projData.projectExecName_str(), 
            "-"+ ', -'.join(options) if len(options) != 0 else ""
        ) # NOTE: Does Order matter of Compile option list?

    # TODO: Support other than Clang!
    def genStr_setTargetLinkOptions(self, projData: ProjectConfigurationData,options:list) -> str:
        return str.format("target_link_options({} PRIVATE $<$<CXX_COMPILER_ID:Clang>: {} > )", 
            projData.projectExecName_str(), 
            "-"+ ', -'.join(options) if len(options) != 0 else ""
        ) # NOTE: Does Order matter of Link option list?

    def genStr_cmake_sourceDirVar(self) -> str:
        return f"{self.genStr_setVar(CMVAR__SOURCE_DIR, CMAKIFY_PathToSourceDir(self.srcDirPath))}"

    def genStr_cmake_sources(self) -> str:         
        return tidy_cmake_string(f"{self.genStr_file_globRecurse_ConfigureDepends(CMVAR__SOURCES,self.getSourcePaths())}")

    def genStr_cmake_headers(self) -> str:                         
        return tidy_cmake_string(f"{self.genStr_file_globRecurse_ConfigureDepends(CMVAR__HEADERS,self.getHeaderPaths())}")

    def genStr_cmake_min_version(self, projdata : ProjectConfigurationData) -> str:
        return f'''cmake_minimum_required(VERSION {projdata.cmakeVersionData.get_major()}.{projdata.cmakeVersionData.get_minor()}.{projdata.cmakeVersionData.get_patch()})'''

    def genStr_cmake_projectdetails(self, projdata : ProjectConfigurationData)->str:    
        
        return tidy_cmake_string(f'''project(            
            {projdata.projectName_str()} 
            VERSION 0.0.1
            DESCRIPTION \"{projdata.projectDesc_str()}\"
            LANGUAGES CXX C)''') #TODO: Let user set VERSION and LANGUAGES

    def genStr_addExecutable(self, projData : ProjectConfigurationData):
        return str.format(f"add_executable({projData.projectExecName_str()})")

    def genStr_file_globRecurse_ConfigureDepends(self, varName : str, dirs :list) -> str:
        return str.format("FILE(GLOB_RECURSE {} CONFIGURE_DEPENDS\n    {}\n)", self.cmakeVars[varName], str.format("\n\t".join(dirs)) )

    def genStr_targetSources(self, projData :ProjectConfigurationData)->str:
        return tidy_cmake_string(
            f'''target_sources({projData.projectExecName_str()}
            PRIVATE
            ${{{self.cmakeVars[CMVAR__SOURCES]}}}
            )'''
        )

    #TODO: Split into several functions
    def genStr_compileSanitizers(self, projData :ProjectConfigurationData, ) -> str:
        return self.genStr_setTargetCompileOptions(projData, {"g", "fsanitize=address,leak,undefined", "fno-omit-frame-pointer", "fsanitize-recover=address",        "fsanitize-blacklist=${CMAKE_CURRENT_SOURCE_DIR}/sanitizer_blacklist.txt"})
        
    def genStr_linkSanitizers(self, projData :ProjectConfigurationData, ) -> str:        
        return self.genStr_setTargetLinkOptions(projData,   {"g", "fsanitize=address,leak,undefined", "fno-omit-frame-pointer", "fsanitize-memory-track-origins=2", "fsanitize-blacklist=${CMAKE_CURRENT_SOURCE_DIR}/sanitizer_blacklist.txt"})        
        
def tidy_cmake_string(string :int = 0)->str:
    splitLines = re.sub(r'^[ \t]+', '', string,0, re.MULTILINE).splitlines()
    ret = '\n'.join(splitLines[0:1])
    ret += '\n'+textwrap.indent(
        '\n'.join(splitLines[1:len(splitLines)]), '\t',predicate=(lambda line, index=0:  line.strip() != '}' and line.strip() != ")" and (index := index+1) == 1 )
    )
    
    return ret