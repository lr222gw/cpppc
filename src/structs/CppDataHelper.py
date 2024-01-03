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
        if os.path.exists(self.cmakeDataHelper.getRelativeCppFilePath(self.projData.entryPointFile_str())) and not self.projData.overwriteProjectTargetDir.getState():
            print(f"Target File ({self.cmakeDataHelper.getRelativeCppFilePath(self.projData.entryPointFile_str())}) Already exists")
        else: 
            with open(self.cmakeDataHelper.getRelativeCppFilePath(self.projData.entryPointFile_str()), "w") as file:                        
                file.write(content)        

    def genStr_includeSystemFile(self, installedFile:str)->str:
        return str.format("#include <{}>\n", installedFile)

    def genStr_includeUserFile(self, localFile:str)->str:
        return str.format("#include \"{}\"\n", localFile)

    def genStr_mainfunc(self, lines :list = [], args :list = ["int argc","char* argv[]"], returnStatement : str = "0")->str:
        ret = "int main("+", ".join(args)+")"
        ret += "{\n"+"\n\t".join(lines)+"\n return "+returnStatement+";\n}"
        return ret
    
    def genStr_FILE_entrypoint(self) -> str:
        ret = self.genStr_includeSystemFile("iostream")
        ret += self.genStr_includeUserFile("generated/cmake_inputs.h") #TODO: do not hardcode
        if self.projData.useCmakeCppBridge.getState() and len(self.cmakeDataHelper.cmakeToCppVars) != 0:
            ret += self.genStr_mainfunc(["std::cout << \"Hello, <<"+self.cmakeDataHelper.cmakeToCppVars[CMVAR__CPPPC_EXAMPLE_BRIDGE_VAR]+"!\" << std::endl;"])
        else :
            ret += self.genStr_mainfunc(["std::cout << \"Hello, World!\" << std::endl;"])
        return ret