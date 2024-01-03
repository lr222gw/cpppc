import os
from .ProjectConfigurationData import ProjectConfigurationData
from .CMakeData import *
from dataclasses import dataclass, field
from .CppCommands import *

@dataclass
class CppDataHelper():
    projData: ProjectConfigurationData
    cmakeDataHelper: CMakeData
    cppCommands : CPPCommandDct = field(default_factory=CPPCommandDct) 

    def __init__(self, projData: ProjectConfigurationData, cmakeDataHelper: CMakeData):
        self.projData = projData
        self.cmakeDataHelper = cmakeDataHelper
        self.cppCommands = CPPCommandDct()

    def genCPPfileContent(self) -> str:
        cppfileStr = ""
        for cmdKeyValList in self.cppCommands.all_cppc.items():
            for cmdKeyVal in self.cppCommands.all_cppc[cmdKeyValList[0]]:
                
                cppfileStr += cmdKeyVal.__str__()

            cppfileStr += "\n"
        return cppfileStr


    def createCppEntryPointFileOnDemand(self) -> str:
        if os.path.exists(self.cmakeDataHelper.getRelativeCppFilePath(self.projData.entryPointFile_str())) and not self.projData.overwriteProjectTargetDir.getState():
            print(f"Target File ({self.cmakeDataHelper.getRelativeCppFilePath(self.projData.entryPointFile_str())}) Already exists")
        else: 
            with open(self.cmakeDataHelper.getRelativeCppFilePath(self.projData.entryPointFile_str()), "w") as file:                        
                file.write(self.genCPPfileContent())        

    def genStr_includeSystemFile(self, installedFile:str)->str:
        return self.cppCommands.add_CPP(
            CPP_INCLUDE_SYS(
                CPPCK_args(installedFile.strip())
            )
        ).__str__()

    def genStr_includeUserFile(self, localFile:str)->str:
        return self.cppCommands.add_CPP(
            CPP_INCLUDE_USR(
                CPPCK_args(localFile.strip())
            )
        ).__str__()

    def genStr_mainfunc(self, lines :list = [], args :list = [CPPCK("int","argc"),CPPCK("char*","argv[]")], returnStatement : str = "0")->str:
        return self.cppCommands.add_CPP_C(
            CPPC_main(
                 args,
                 *lines, CPP_CUSTOMLINE("return "+returnStatement)
            )
        ).__str__()

    def genStr_FILE_entrypoint(self) -> str:
        ret = self.genStr_includeSystemFile("iostream")
        ret += self.genStr_includeUserFile("generated/cmake_inputs.h") #TODO: do not hardcode
        ret += self.genStr_mainfunc([CPP_CUSTOMLINE("std::cout << \"Hello, \"<<"+self.cmakeDataHelper.cmakeToCppVars[CMVAR__CPPPC_EXAMPLE_BRIDGE_VAR]+"<<\"!\" << std::endl")])
        return ret
