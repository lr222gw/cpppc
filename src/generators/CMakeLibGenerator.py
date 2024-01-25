from genericpath import isdir
from os import path
import os
import re
from typing import Union
from src.structs.CMakeDataHelper import *
from src.structs.ProjectConfigurationDat import *
import PyQt5.Qt 
import PyQt5.QtWidgets

def cmakeifyLib(libDirPath: str) -> tuple[str, CMakeDataHelper]:
    headerList = list[str]()
    sourceList = list[str]()
    filePaths = list[str]()

    #TODO: Make sure that we're not messing up somones library... maybe double check if there's already a CMakeLists that we didnt create...

    # If library located in current directory
    if path.commonpath([os.getcwd(),path.abspath(libDirPath)]) == os.getcwd():
         libDirPath = f"./{path.relpath(libDirPath)}"
    
    projectName =  path.basename(libDirPath) #TODO: CMake might have requirements for legal CMakeProject names...
    

    projDat = ProjectConfigurationData(
        projectName                = projectName,
        projectTargetDir           = os.path.join(libDirPath, os.pardir),
        projectExecName            = projectName+"_lib",
        projectDesc                = f"Generated CMake project for {projectName}",
        entryPointFile             = None,
        overwriteProjectTargetDir  = None,
        useProgram_ccache          = False,
        useMeasureCompiletime      = False,
        cmakeVersionData           = (3,28,0),# TODO: fix  hardcode...
        cmakeToCppVars             = dict[str,tuple[str,str]](),
        linkLibs                   = dict[str,tuple[str,bool, list[str],TargetDatas]](), 
        linkLibs_public            = list[str](),
        linkLibs_private           = list[str](),
        props                      = dict[str,str|bool|int]()
    )    

    cmakelist = CMakeDataHelper()
    cmakelist.runtimeInit(projDat)
    
    __getFilePaths(libDirPath,libDirPath,filePaths)

    def isHeaderFile(file: str) -> bool:
         return path.splitext(file)[1] in [".h", ".hpp", ".hxx"]
    
    def isSourceFile(file: str) -> bool:
         return path.splitext(file)[1] in [".c", ".cpp", ".cc", ".cxx"]
    
    def fileInPaths(realpath:str, filePaths:list[str]):
        for p in filePaths :
            if path.commonpath([realpath.upper(), p.upper()]) == p.upper(): 
                return True
            
        return  False
    
    def dirInRoot_wildcard(realpath:str, filePaths:list[str]):
    
        for p in filePaths :
            pathWildcard = re.compile(fr"[^/]*{p}[^/]*/.*")
            if re.match(pathWildcard, realpath) != None: 
                return True
            
        return  False
                 
    def isInGeneratedDir(file:str) -> bool:
        generatedpaths = ["build", ".cache", ".github"]
        return fileInPaths(file , generatedpaths)
    
    def isTest(file:str) -> bool:
        testpaths = ["test", "tests", "testfiles", "testing", "test-suite", "testsuite"]
        return dirInRoot_wildcard(file , testpaths)
    
    def isUnlikely(file:str) -> bool:
        testpaths = ["tools","third_party", "deprecated", "examples", "example", "bench" "benchmark", "benchmarks", "demo", "demos", "sample", "samples","documentation", "docs", "doc", "media", "medias"]
        return dirInRoot_wildcard(file , testpaths)
    
    #TODO: Better name...
    def isUseable(file:str) -> bool:        

        if not isHeaderFile(file) and not isSourceFile(file):
             return False

        if(isTest(file)):
             return False
        
        if(isInGeneratedDir(file)):
             return False        
        
        if(isUnlikely(file)):
             return False

        return True
    
    filteredFiles : list[str] = [filePath for filePath in filePaths if isUseable(filePath)]
    
    headerFiles : list[str] = ["\"${CMAKE_CURRENT_SOURCE_DIR}/"+filePath+"\"" for filePath in filteredFiles if isHeaderFile(filePath)]
    sourceFiles : list[str] = ["\"${CMAKE_CURRENT_SOURCE_DIR}/"+filePath+"\"" for filePath in filteredFiles if isSourceFile(filePath)]
    sources_headers = list[str]()
    sources_headers.extend(sourceFiles)
    sources_headers.extend(headerFiles)    

    headerOnlyLib :bool = False
    if len(sourceFiles) == 0:
        headerOnlyLib = True
    
    if headerOnlyLib and len(headerFiles) == 0:
        terminate("Provided library path does not contain header or source files!")
        #TODO: Replace terminate with WarnUser

    cmakelist.genStr_cmake_min_version()
    cmakelist.genStr_cmake_projectdetails()


    if headerOnlyLib == True:
        cmakelist.genStr_addLibrary(libraryType=LibraryType.INTERFACE)
        
    else :
        cmakelist.genStr_addLibrary(libraryType=LibraryType.STATIC)  
        cmakelist.genStr_targetSources(projDat.projectExecName, sources_headers)


    commonHeaderPath = path.commonpath([h.replace("\"", "") for h in headerFiles])
    cmakelist.genStr_targetIncludeDirectories(projDat.projectExecName,True, commonHeaderPath)    

    with open(cmakelist.targetDirPath+"/"+"CMakeLists.txt", "w") as file:
            file.write(cmakelist.genCMakeList())

    return (projDat.projectExecName, cmakelist)

def __getFilePaths(librootpath:str,currentDirPath: str, filePaths:list[str]):

    if(path.isdir(currentDirPath)):
        for file in os.listdir(path.abspath(currentDirPath)): 

            file_absPath = path.join(path.abspath(currentDirPath),file)
            if path.isfile(file_absPath):

                pathRelativeToLib = path.relpath(path.join(currentDirPath,file), librootpath)
                
                filePaths.append(pathRelativeToLib)
                pass 
            else: 
                __getFilePaths(librootpath,file_absPath, filePaths)

