from dataclasses import dataclass, field
from .CMakeVersionData import CMakeVersionData
from .GuiData import GuiData, GuiDataToggle



@dataclass
class ProjectConfigurationData: 
    projectName :       GuiData= field(default= GuiData)
    def projectName_str(self) -> str:
        return self.projectName.widget.text()

    projectTargetDir :  GuiData= field(default= GuiData)
    def projectTargetDir_str(self) -> str:
        return self.projectTargetDir.widget.text()

    projectExecName :   GuiData= field(default= GuiData)
    def projectExecName_str(self) -> str:
        return self.projectExecName.widget.text()

    projectDesc :       GuiData= field(default= GuiData)
    def projectDesc_str(self) -> str:
        return self.projectDesc.widget.toPlainText()

    overwriteProjectTargetDir : GuiDataToggle = field(default= GuiDataToggle)    

    #TODO: put inside a vector, enable user to use multiple prgorams...
    useProgram_ccache : GuiDataToggle = field(default= GuiDataToggle)

    #TODO: Split sanitizers into Memory and address sanitizers
    useSanitizers : GuiDataToggle = field(default= GuiDataToggle)


    useMeasureCompiletime : GuiDataToggle = field(default= GuiDataToggle)
        

    def getTargetPath(self) -> str:
        path = self.projectTargetDir.widget.text() +  "/" + self.projectName.widget.text()
        return path

    cmakeVersionData :  CMakeVersionData = field(default=CMakeVersionData)
    def toString(self):
        print(f"ProjectName:{self.projectName.widget.text()}")
        print(f"projectTargetDir:{self.projectTargetDir.widget.text()}")
        print(f"projectExecName:{self.projectExecName.widget.text()}")
        print(f"projectDesc:{self.projectDesc.widget.toPlainText()}")
        print(f"cmakeVersionData.major:{self.cmakeVersionData.get_major()}")
        print(f"cmakeVersionData.minor:{self.cmakeVersionData.get_minor()}")
        print(f"cmakeVersionData.patch:{self.cmakeVersionData.get_patch()}")
