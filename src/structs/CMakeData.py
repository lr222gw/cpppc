import re
import textwrap
from .ProjectConfigurationData import ProjectConfigurationData
from dataclasses import dataclass, field

CMVAR__SOURCE_DIR : str   = "_SOURCE_DIR"
CMVAR__SOURCES    : str   = "_SOURCES"
CMVAR__HEADERS    : str   = "_HEADERS"

CMVAR__CPPPC_EXAMPLE_BRIDGE_VAR : str = "CPPPC_EXAMPLE_BRIDGE_VAR"
CMFUNC__add_cmake_inputs_to_targets : str = "add_cmake_inputs_to_targets"

CMAKE_CURRENT_SOURCE_DIR = "${CMAKE_CURRENT_SOURCE_DIR}"

def CMAKIFY_PathToSourceDir(path:str) -> str:
    return str.format("{}",CMAKE_CURRENT_SOURCE_DIR+"/"+path)

@dataclass
class CMakeData : 
    cmakelist_str : str = "#CMakeLists.txt created through CPPPC\n"
    # Directory Paths 
    targetDirPath   :str = "."
    srcDirPath      :str = "src"
    cmakeDirPath    :str = "cmake"
    cmakeGenSrcDirPath: str = srcDirPath + "/generated" #TODO avoid hardcoding...
    
    FILE_cmake_cpp_data     :str = "cmake_cpp_data.cmake"
    FILE_cmake_inputs_h_in  :str = "cmake_inputs.h.in"
    FILE_cmake_inputs_h     :str = "cmake_inputs.h"

    cmakeFuncs : dict = field(default_factory=dict)
    cmakeVars : dict = field(default_factory=dict)


    def genStr_FILE_cmake_cpp_data(self, projDat :ProjectConfigurationData):
        targetArg = "target"
        ret = self.genStr_setVarString(CMVAR__CPPPC_EXAMPLE_BRIDGE_VAR, "Example string from CMake to C++") + "\n"
        ret += self.genStr_function(CMFUNC__add_cmake_inputs_to_targets, 
            [targetArg, "varValue"],
            [
                self.genStr_setVarString(CMVAR__CPPPC_EXAMPLE_BRIDGE_VAR, r"${varValue}"),
                self.genStrHlp_generateHeaderFileInBuildDir(targetArg)
            ]
        )        
        return ret    

    def genStrHlp_generateHeaderFileInBuildDir(self, targetVar) -> str: 
        ret = tidy_cmake_string(
            self.genStr_configureFile(
                pathify([self.cmakeDirPath,self.FILE_cmake_inputs_h_in]),
                pathify([CMAKE_CURRENT_SOURCE_DIR,self.cmakeGenSrcDirPath,self.FILE_cmake_inputs_h])
                ),
                0
                )
        ret += tidy_cmake_string(
            self.genStr_targetIncludeDirectories(
                str.format("${{{}}}",targetVar),
                pathify([CMAKE_CURRENT_SOURCE_DIR, self.cmakeGenSrcDirPath])
                ),
                0
                )

        ret += tidy_cmake_string(
            self.genStr_targetSources(                
                str.format("${{{}}}",targetVar),
                [
                    pathify([CMAKE_CURRENT_SOURCE_DIR,self.cmakeGenSrcDirPath,self.FILE_cmake_inputs_h])
                ]
            ),0
            
        )
        return ret

    def genStr_configureFile(self, inputFile :str, outputFile :str)->str:
        return str.format("configure_file({} {})",inputFile,outputFile)

    def genStr_function(self, functionName : str, arguments:list, lines : list) -> str:
        ret = f"function({functionName} {' '.join(arguments)})\n"
        ret += "\t" +'\n\t'.join(lines) + '\n'
        ret += "endfunction()"
        return ret

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

    def initCmakeVars(self,projData : ProjectConfigurationData):        
        self.cmakeVars[CMVAR__SOURCE_DIR] = projData.projectName_str() + CMVAR__SOURCE_DIR
        self.cmakeVars[CMVAR__SOURCES]    = projData.projectName_str() + CMVAR__SOURCES
        self.cmakeVars[CMVAR__HEADERS]    = projData.projectName_str() + CMVAR__HEADERS
        self.cmakeVars[CMVAR__CPPPC_EXAMPLE_BRIDGE_VAR] = CMVAR__CPPPC_EXAMPLE_BRIDGE_VAR

    def initCmakeFuncs(self,projData : ProjectConfigurationData):        
        self.cmakeFuncs[CMVAR__SOURCE_DIR] = projData.projectName_str() + CMVAR__SOURCE_DIR        

    def genStr_setVar(self, varName:str,varValue:str) -> str:
        return str.format("set({} {})", self.cmakeVars[varName], str.format("{}",varValue))

    def genStr_setVarString(self, varName:str,varValue:str) -> str:
        return str.format("set({} {})", self.cmakeVars[varName], str.format("\"{}\"",varValue))

    def genStr_setProperty(self, projData: ProjectConfigurationData, propertyName:str, propertyValue:str) -> str:
        return str.format("set_property(TARGET {} PROPERTY {} \"{}\")", 
            projData.projectExecName_str(), 
            propertyName,
            propertyValue
        )

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

    def genStr_targetSources(self, target:str, sources :list) ->str : 
        return "target_sources({} PRIVATE \n\t{}\n)".format(target,'\n\t'.join(sources))

    def genStr_targetIncludeDirectories(self, target:str, dirPath :str) ->str : 
        return f"target_include_directories({target} PRIVATE {dirPath})"

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
        return str.format("FILE(GLOB_RECURSE {} CONFIGURE_DEPENDS\n    {}\n)", self.cmakeVars[varName], "\n\t".join(dirs) )

    def genStrHlp_addingProjectsTargetSources(self, projData :ProjectConfigurationData)->str:
        return tidy_cmake_string(
            self.genStr_targetSources(projData.projectExecName_str(), [str.format("${{{}}}",self.cmakeVars[CMVAR__SOURCES])] )

        )

    #TODO: Split into several functions
    def genStr_compileSanitizers(self, projData :ProjectConfigurationData, ) -> str:
        return self.genStr_setTargetCompileOptions(projData, {"g", "fsanitize=address,leak,undefined", "fno-omit-frame-pointer", "fsanitize-recover=address",        "fsanitize-blacklist=${CMAKE_CURRENT_SOURCE_DIR}/sanitizer_blacklist.txt"})
        
    def genStr_linkSanitizers(self, projData :ProjectConfigurationData, ) -> str:        
        return self.genStr_setTargetLinkOptions(projData,   {"g", "fsanitize=address,leak,undefined", "fno-omit-frame-pointer", "fsanitize-memory-track-origins=2", "fsanitize-blacklist=${CMAKE_CURRENT_SOURCE_DIR}/sanitizer_blacklist.txt"})        
        
    def genStr_compileTimeProperty(self, projData :ProjectConfigurationData, ) -> str:
        return self.genStr_setProperty(projData, "RULE_LAUNCH_COMPILE", "${CMAKE_COMMAND} -E time}")

    def genStr_cppProperties(self, projData:ProjectConfigurationData) -> str:
        ret = f"set_target_properties({projData.projectExecName_str()} PROPERTIES\n"
        maxSpace=max(len(cmakeProp.cmake_propName) for cmakeProp in projData.props) + 1 # +1 is padding
        ret += "\n".join(
                cmakeProp.cmake_propName.ljust(maxSpace) + str(cmakeProp.getValue())
                for cmakeProp in projData.props 
            ) + "\n)"
        return tidy_cmake_string(ret)

def tidy_cmake_string(string :str, linesToSkip:int = 1)->str:
    splitLines = re.sub(r'^[ \t]+', '', string,0, re.MULTILINE).splitlines()
    ret = '\n'.join(splitLines[0:linesToSkip])
    ret += '\n'+textwrap.indent(
        '\n'.join(splitLines[linesToSkip:len(splitLines)]), '\t',predicate=(lambda line, index=0:  line.strip() != '}' and line.strip() != ")" and (index := index+1) == 1 )
    )
    
    return ret

def pathify(strings :list) -> str:
        return "/".join(strings)    