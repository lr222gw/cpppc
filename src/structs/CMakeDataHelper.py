import enum
import os
import pathlib
import re
import textwrap

#from src.structs.GuiData import library_inputWidget
from .ProjectConfigurationGUI import ProjectConfigurationGUI
from .ProjectConfigurationDat import ProjectConfigurationData, TargetDatas
from dataclasses import dataclass, field
from .CMakeCommands import *

class LibraryType(enum.StrEnum):
    INTERFACE   = "INTERFACE"
    SHARED      = "SHARED"
    STATIC      = "STATIC"

CMVAR__SOURCE_DIR : str   = "_SOURCE_DIR"
CMVAR__SOURCES    : str   = "_SOURCES"
CMVAR__HEADERS    : str   = "_HEADERS"

CMVAR__CPPPC_EXAMPLE_BRIDGE_VAR : str = "CPPPC_EXAMPLE_BRIDGE_VAR"
CMFUNC__add_cmake_inputs_to_targets : str = "add_cmake_inputs_to_targets"

CMAKE_CURRENT_SOURCE_DIR = "${CMAKE_CURRENT_SOURCE_DIR}"

def CMAKIFY_PathToSourceDir(path:str) -> str:
    return str.format("{}",CMAKE_CURRENT_SOURCE_DIR+"/"+path)

@dataclass
class CMakeDataHelper : #TODO: Rename this to CMakeDataManager or similar...
    cmakelist_str : str = "#CMakeLists.txt created through CPPPC\n"
    # Directory Paths 
    targetDirPath   :str = "."
    depsDirPath     :str = "deps"
    srcDirPath      :str = "src"
    cmakeDirPath    :str = "cmake"
    cmakeGenSrcDirPath: str = srcDirPath + "/generated" #TODO avoid hardcoding...
    
    FILE_cmake_cpp_data     :str = "cmake_cpp_data.cmake"
    FILE_cmake_inputs_h_in  :str = "cmake_inputs.h.in"
    FILE_cmake_inputs_h     :str = "cmake_inputs.h"

    cmakeFuncs : dict = field(default_factory=dict)
    cmakeVars  : dict = field(default_factory=dict)
    cmakeToCppVars : dict = field(default_factory=dict)

    cmakeCommands : CMakeCommandDct= field(default_factory=CMakeCommandDct)

    projdata_OLD : ProjectConfigurationGUI = field(default_factory=ProjectConfigurationGUI)
    projdata : ProjectConfigurationData = field(default_factory=ProjectConfigurationData)

    def __init__(self):
        self.projdata = ProjectConfigurationData()
        self.cmakeVars = dict()
        self.cmakeFuncs = dict()
        self.cmakeToCppVars = dict()
        self.cmakeCommands = CMakeCommandDct()


    def runtimeInit(self, projdata : ProjectConfigurationData):
        self.projdata = projdata
        self.setTargetDirPaths(self.projdata.getTargetPath())
        self.cmakeVars.clear()
        self.cmakeFuncs.clear()
        self.cmakeToCppVars.clear()
        self.cmakeCommands.clear()

        self.initCmakeVars()
        self.initCmakeFuncs()

    def appendOrder(self, cmakeCommandType : Type):
        self.cmakeCommands.appendOrder(cmakeCommandType)

    def genCMakeList(self):

        cmakeListStr = ""
        for cmdKeyValList in self.cmakeCommands.all_cmc.items():
            for cmdKeyVal in self.cmakeCommands.all_cmc[cmdKeyValList[0]]:
                
                cmakeListStr += cmdKeyVal.__str__() + "\n"

            cmakeListStr += "\n"

        return cmakeListStr

    def getRelativeCMakeFilePath(self, file): #NOTE: Relative from CPPPC, not from Project Root...
        return os.path.join(self.targetDirPath,self.cmakeDirPath,file)
    
    def getRelativeCppFilePath(self, file): #NOTE: Relative from CPPPC, not from Project Root...
        return os.path.join(self.targetDirPath, self.srcDirPath,file)

    def genStr_FILE_cmake_inputs_h_in(self):
        ret = self.genStr_cmake_cpp_defines()
        return ret

    def genStr_cmake_cpp_defines(self):
        ret = "#define " + "#define ".join([f'{key}  \"@{val}@\"\n' for key, val in self.cmakeToCppVars.items()])
        return ret

    def genStr_callFunction(self, functionName : str, arguments:list) ->str:
        return self.cmakeCommands.add_CMC(
            CMC_CALLFUNC(functionName,
                CMCK_args(arguments)
            )
        ).__str__()

    def genStr_FILE_cmake_cpp_data(self):
        targetArg = "target"
        ret = self.genStr_setVarString_cmakeToCpp(CMVAR__CPPPC_EXAMPLE_BRIDGE_VAR, "Example string from CMake (v.${CMAKE_VERSION}) to C++") + "\n"
        ret += self.genStr_function(CMFUNC__add_cmake_inputs_to_targets, 
            [targetArg],
            [
                self.genStrHlp_generateHeaderFileInBuildDir(False, targetArg) #TODO: Uncertain if False is the best default value...
            ]
        )        
        return ret    

    def genStrHlp_generateHeaderFileInBuildDir(self, isPublic : bool,  targetVar) -> str: 
        ret = tidy_cmake_string(
            self.genStr_configureFile(
                str((pathlib.Path(self.cmakeDirPath) / self.FILE_cmake_inputs_h_in).as_posix()),
                str((pathlib.Path(CMAKE_CURRENT_SOURCE_DIR) / self.cmakeGenSrcDirPath / self.FILE_cmake_inputs_h).as_posix())
                ),
                0
                )
        ret += tidy_cmake_string(
            self.genStr_arg_targetIncludeDirectories(
                str.format("${{{}}}",targetVar),
                isPublic,
                str((pathlib.Path(CMAKE_CURRENT_SOURCE_DIR) / self.cmakeGenSrcDirPath).as_posix())
                ),
                0
                )

        ret += tidy_cmake_string(
            self.genStr_targetSources(                
                str.format("${{{}}}",targetVar),
                [
                    str((pathlib.Path(CMAKE_CURRENT_SOURCE_DIR) / self.cmakeGenSrcDirPath / self.FILE_cmake_inputs_h).as_posix())
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

    def getCMakeListStr(self) -> str:
        return self.cmakelist_str
    
    def getPathInTarget(self, targetInsidePath : str) -> str:
        return self.targetDirPath + "/" + targetInsidePath
    
    def getLocalPathInDeps(self, targetInsidePath : str) -> str:
        return self.depsDirPath + "/" + targetInsidePath

    def getSourcePaths(self) ->list:
        return [
            CMAKIFY_PathToSourceDir(self.srcDirPath)+"/*.cpp",
            CMAKIFY_PathToSourceDir(self.srcDirPath)+"/*.c",
            CMAKIFY_PathToSourceDir(self.srcDirPath)+"/*.hpp",
            CMAKIFY_PathToSourceDir(self.srcDirPath)+"/*.h",
        ]
    
    def getHeaderPaths(self) ->list:
        return [
            CMAKIFY_PathToSourceDir(self.srcDirPath)+"/*.hpp",
            CMAKIFY_PathToSourceDir(self.srcDirPath)+"/*.h",
        ]

    def initCmakeVars(self):        
        self.cmakeVars[CMVAR__SOURCE_DIR] = self.projdata.projectName + CMVAR__SOURCE_DIR
        self.cmakeVars[CMVAR__SOURCES]    = self.projdata.projectName + CMVAR__SOURCES
        self.cmakeVars[CMVAR__HEADERS]    = self.projdata.projectName + CMVAR__HEADERS
        
        self.cmakeToCppVars[CMVAR__CPPPC_EXAMPLE_BRIDGE_VAR] = CMVAR__CPPPC_EXAMPLE_BRIDGE_VAR
        for name, val in self.projdata.cmakeToCppVars.items() :
            self.cmakeToCppVars[val[0]] = val[1]


    def initCmakeFuncs(self):
        self.cmakeFuncs[CMVAR__SOURCE_DIR] = self.projdata.projectName + CMVAR__SOURCE_DIR        

    def genStr_includeCmakeFile(self, cmakeFile : str) -> str:
        return self.cmakeCommands.add_CMC(
            CMC_include(
                CMCK_args(str((pathlib.Path(self.cmakeDirPath) / cmakeFile).as_posix()))
            )
        ).__str__()

    def genStr_setVar(self, varName:str,varValue:str) -> str:
        return self.cmakeCommands.add_CMC(           
                CMC_set(
                    CMCK(self.cmakeVars[varName],str.format("{}",varValue))
                )
        ).__str__()

    def genStr_setVarString(self, varName:str,varValue:str) -> str:
        return str.format("set({} {})", self.cmakeVars[varName], str.format("\"{}\"",varValue))


    def genStr_setVar_cmakeToCpp(self, varName:str,varValue:str) -> str:
        return str.format("set({} {})", self.cmakeToCppVars[varName], str.format("{}",varValue))

    def genStr_setVarString_cmakeToCpp(self, varName:str,varValue:str) -> str:
        return str.format("set({} {})", self.cmakeToCppVars[varName], str.format("\"{}\"",varValue))

    def genStr_setProperty(self, propertyName:str, propertyValue:str) -> str:
        return self.cmakeCommands.add_CMC(
            CMC_set_property(
                CMCK("TARGET", self.projdata.projectExecName),
                CMCK("PROPERTY"),
                CMCK_str(propertyName, propertyValue)
            )
        ).__str__()

    def genStr_find_program(self, name:str, name_var:str) -> str:    
        return self.cmakeCommands.add_CMC(
            CMC_find_program(
                CMCK(name, name_var)
            )
        ).__str__()

    def addCMakeCompilerLauncher(self, programName : str) -> str:        
        name_var=f"{programName}_program_var"
        content= self.genStr_find_program(programName, name_var)+"\n"
        content += self.genStr_if(
            name_var,            
            CMC_set(
                CMCK_str("CMAKE_CXX_COMPILER_LAUNCHER", CMVAR_REF(name_var))
            )            
        ) + "\n"
        return content

    def genStr_if(self,condition, *body):
        return self.cmakeCommands.add_CMC_C(
            CMCC_if(
                CMCK(condition),
                *body
            )
        ).__str__()

    # TODO: Support other than Clang!
    def genStr_setTargetCompileOptions(self, options:list) -> str:
        return self.cmakeCommands.add_CMC(
            CMC_target_compile_options(
                CMCK(self.projdata.projectExecName),
                CMCK("PRIVATE", CM_generatorExpressionConditional("CXX_COMPILER_ID:Clang", *options))
            )
        ).__str__()

    # TODO: Support other than Clang!
    def genStr_setTargetLinkOptions(self, options:list) -> str:
        return self.cmakeCommands.add_CMC(
            CMC_target_link_options(
                CMCK(self.projdata.projectExecName),
                CMCK("PRIVATE", CM_generatorExpressionConditional("CXX_COMPILER_ID:Clang", *options))
            )
        ).__str__()

    def _referenceCorrectifier(self, ref):

        if "::" in ref or "-" in ref: 
            return ref 
        else:
            return f"${{{ref}}}"

    def genStr_targetLinkLibraries(self) -> str:
        return self.cmakeCommands.add_CMC(
            CMC_target_link_libraries(
                CMCK(self.projdata.projectExecName),
                CMCK("PUBLIC",  [self._referenceCorrectifier(l) for k,v in self.projdata.linkLibs_public.items()  for l in v]), 
                CMCK("PRIVATE", [self._referenceCorrectifier(l) for k,v in self.projdata.linkLibs_private.items() for l in v]) 
            )
        ).__str__()

    def genStr_targetSources(self, target:str, sources :list) ->str : 
        return self.cmakeCommands.add_CMC(
            CMC_target_sources(
                CMCK(target),
                CMCK("PRIVATE", sources)
            )
        ).__str__()
    
    def genStr_targetIncludeDirectories(self) ->str : 
        return self.cmakeCommands.add_CMC(
            CMC_target_include_directories(
                CMCK(self.projdata.projectExecName),
                CMCK("PUBLIC",  [self._referenceCorrectifier(l) for k,v in self.projdata.linkIncl_public.items()  for l in v]), 
                CMCK("PRIVATE", [self._referenceCorrectifier(l) for k,v in self.projdata.linkIncl_private.items() for l in v]) 
            )
        ).__str__()

    def genStr_arg_targetIncludeDirectories(self, target:str, isPublic:bool, *dirPaths :str) ->str : 
        return self.cmakeCommands.add_CMC(
            CMC_target_include_directories(
                CMCK(target),
                CMCK("PUBLIC" if isPublic else "PRIVATE", *dirPaths)
            )
        ).__str__()
    
    def genStr_cmake_find_packages(self):
        if self.projdata.linkLibs != None:
            for key, findPackage in self.projdata.linkLibs.items():
                targetData :TargetDatas = findPackage[3]

                findPackageNewName = targetData.find_package
                if key in self.projdata._linkLibs_findPackage:
                    findPackageNewName = self.projdata._linkLibs_findPackage[key]
                
                if findPackageNewName != None: 
                    components = self.projdata.getLibComponents(key)
                    if len(components) > 0:
                        self.cmakeCommands.add_CMC(
                            CMC_find_package(
                                CMCK(findPackageNewName, "REQUIRED"),
                                CMCK("COMPONENTS", " ".join(components))
                            )
                        )
                    else: 
                        self.cmakeCommands.add_CMC(
                            CMC_find_package(
                                CMCK(findPackageNewName, "REQUIRED")
                            )
                        )
    
    def genStr_cmake_sourceDirVar(self) -> str:
        return f"{self.genStr_setVar(CMVAR__SOURCE_DIR, CMAKIFY_PathToSourceDir(self.srcDirPath))}"
    
    def genStr_cmake_sources(self) -> str:         
        return tidy_cmake_string(f"{self.genStr_file_globRecurse_ConfigureDepends(CMVAR__SOURCES,self.getSourcePaths())}")

    def genStr_cmake_headers(self) -> str:                         
        return tidy_cmake_string(f"{self.genStr_file_globRecurse_ConfigureDepends(CMVAR__HEADERS,self.getHeaderPaths())}")

    def genStr_cmake_min_version(self) -> str:
        return self.cmakeCommands.add_CMC(
            CMC_cmake_minimum_required(
                CMCK("VERSION", self.projdata.cmakeVersionData[0], self.projdata.cmakeVersionData[1], self.projdata.cmakeVersionData[2]),
            )
        ).__str__()

    def genStr_cmake_projectdetails(self)->str:
        return self.cmakeCommands.add_CMC(
                CMC_project(
                    CMCK(self.projdata.projectName),
                    CMCK("VERSION", "0.0.1"), #TODO: Let User set VERSION
                    CMCK_str("DESCRIPTION", self.projdata.projectDesc),
                    CMCK("LANGUAGES", "CXX C") #TODO: Let user set LANGUAGES
                )
            ).__str__()

    def genStr_addExecutable(self):
        return self.cmakeCommands.add_CMC(CMC_add_executable(CMCK(self.projdata.projectExecName))).__str__()
    
    def genStr_addLibrary(self, libraryType : LibraryType):            
        return self.cmakeCommands.add_CMC(CMC_add_library(CMCK(self.projdata.projectExecName, libraryType))).__str__()
    
    def genStr_addSubdirectory(self, subdir:str):
        return self.cmakeCommands.add_CMC(CMC_add_subdirectory(CMCK(subdir))).__str__()

    def genStr_file_globRecurse_ConfigureDepends(self, varName : str, dirs :list) -> str:                
        return self.cmakeCommands.add_CMC(
            CMC_file(
                    CMCK("GLOB_RECURSE",self.cmakeVars[varName]),
                    CMCK("CONFIGURE_DEPENDS",  dirs)
                )).__str__()

    def genStrHlp_addingProjectsTargetSources(self)->str:
        return tidy_cmake_string(
            self.genStr_targetSources(self.projdata.projectExecName, [str.format("${{{}}}",self.cmakeVars[CMVAR__SOURCES])] )

        )

    #TODO: Split into several functions
    def genStr_compileSanitizers(self, *args ) -> str:
        return self.genStr_setTargetCompileOptions(list(args))
        
    def genStr_linkSanitizers(self,*args) -> str:        
        return self.genStr_setTargetLinkOptions(list(args))
        
    def genStr_compileTimeProperty(self ) -> str:
        return self.genStr_setProperty("RULE_LAUNCH_COMPILE", "${CMAKE_COMMAND} -E time")

    def genStr_cppProperties(self) -> str:
        return self.cmakeCommands.add_CMC(
            CMC_set_target_properties(
                CMCK(self.projdata.projectExecName),
                CMCK(
                    "PROPERTIES", 
                    propifyList(self.projdata.props)
                )
            ),            
        ).__str__()

def tidy_cmake_string(string :str, linesToSkip:int = 1)->str:
    splitLines = re.sub(r'^[ \t]+', '', string,0, re.MULTILINE).splitlines()
    ret = '\n'.join(splitLines[0:linesToSkip])
    ret += '\n'+textwrap.indent(
        '\n'.join(splitLines[linesToSkip:len(splitLines)]), '\t',predicate=(lambda line, index=0:  line.strip() != '}' and line.strip() != ")" and (index := index+1) == 1 )
    )
    
    return ret