from dataclasses import dataclass, field
from .CMakeVersionData import CMakeVersionData
from .GuiData import GuiData, GuiDataToggle, GuiDataComboBox
from .. import helper_funcs as hlp



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

    useCmakeCppBridge : GuiDataToggle = field(default= GuiDataToggle)

    #Properties 
    props :list = field(default_factory=list)
    def addProp_checkbox(self, label:str, cmakePropName:str,cmakePropValue:bool, parentLayout) -> GuiDataToggle:
        datToggle = hlp.addCheckBox(label,cmakePropValue,parentLayout)
        datToggle.cmake_propName = cmakePropName        
        datToggle.setValue(cmakePropValue)
        self.props.append(datToggle)

    def addProp_combobox_list(self, label:str, cmakePropName:str,cmakePropValues:list, defaultChoice:int, parentLayout) -> GuiDataComboBox:
        datComboboxList = hlp.addComboBox_list(label,cmakePropValues,parentLayout)
        datComboboxList.cmake_propName = cmakePropName
        # datToggle.widget.setState(cmakePropValue)
        
        datComboboxList.setValue(defaultChoice)
        self.props.append(datComboboxList)
    
        

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
