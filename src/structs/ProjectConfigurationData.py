from typing import Tuple
from dataclasses import dataclass, field
from typing import Callable
from .CMakeVersionData import CMakeVersionData
from .GuiData import *
from .. import helper_funcs as hlp
from .CMakeCommands import *

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

    entryPointFile :   GuiData= field(default= GuiData)
    def entryPointFile_str(self) -> str:
        return self.entryPointFile.widget.text()

    overwriteProjectTargetDir : GuiDataToggle = field(default= GuiDataToggle)    

    #TODO: put inside a vector, enable user to use multiple prgorams...
    useProgram_ccache : GuiDataToggle = field(default= GuiDataToggle)

    #TODO: Split sanitizers into Memory and address sanitizers
    useSanitizers : GuiDataToggle = field(default= GuiDataToggle)

    useMeasureCompiletime : GuiDataToggle = field(default= GuiDataToggle)

    useCmakeCppBridge : GuiDataToggle = field(default= GuiDataToggle)

    cmakeToCppVars : dict = field(default_factory=dict)

    publicLinkLibs :list = field(default_factory=list)
    privateLinkLibs:list = field(default_factory=list)

    extraFeatures :list[FeatureToggle] = field(default_factory=list[FeatureToggle])
    extraFeaturesShared :list[FeatureShareToggle] = field(default_factory=list[FeatureShareToggle])
    def initExtraFeatures(self):
        self.__initExtraFeature()
        self.__initExtraFeatureShared()
    def __initExtraFeature(self):
        for feature in self.extraFeatures:
            feature.functionWrapper()
    def __initExtraFeatureShared(self):
        for feature in self.extraFeaturesShared:
            for functionWrapper in feature.functionWrappers:
                functionWrapper()

    def getPathInTarget(self, targetInsidePath : str) -> str:
        return self.getTargetPath() + "/" + targetInsidePath
         

    def addExtraFeature_checkbox(self, label:str, value :str, featureDefaultState:bool, parentLayout) -> FeatureToggle: 
        datToggle = hlp.addFeature_CheckBox(label,value, featureDefaultState, parentLayout)
        datToggle.setState(featureDefaultState)
        self.extraFeatures.append(datToggle)
        return datToggle

    def __addExtraFeature_subCheckbox(self, label:str, value :str, featureDefaultState:bool, parentLayout, requirement:Optional[Callable]) -> FeatureToggle: 
        datToggle = hlp.addFeature_CheckBox(label,value, featureDefaultState, parentLayout)
        datToggle.setState(featureDefaultState)
        datToggle.requirement=requirement
        return datToggle
    
    def __addExtraFeatureShare_subCheckbox(self, label:str, value :str, featureDefaultState:bool, parentLayout, requirement:Optional[Callable]) -> FeatureShareToggle: 
        datToggle = hlp.addFeatureShare_CheckBox(label,value, featureDefaultState, parentLayout)
        datToggle.setState(featureDefaultState)
        datToggle.requirement=requirement
        return datToggle

    def addExtraFeatureGroup_checkbox(self, groupParentLayout, groupCheckBoxParentLayout, groupName : str, checkBoxName : str, defaultState:bool, genStrFunc : Callable, *ToggleDatas : ToggleData) -> FeatureGroup : 
        groupToggle = hlp.addCheckBox(checkBoxName,defaultState,groupCheckBoxParentLayout)
        groupLayout = hlp.addHidableGroup(
            groupParentLayout,
            groupCheckBoxParentLayout,
            groupName,
            groupToggle
        )
        # Use the regular GuiToggle as arg, create a Feature Toggle
        featureGroupToggle = FeatureGroup(
            groupToggle,
            functionWrapper=hlp.strListFactory(genStrFunc, groupToggle, *[self.__addExtraFeature_subCheckbox(data.name, data.val, data.defaultValue, groupLayout, requirement=data.requirement) for data in ToggleDatas]),
            featureName=groupName
        )
        self.extraFeatures.append(featureGroupToggle)
        return featureGroupToggle

    def addExtraFeatureShareGroup_checkbox(self, groupParentLayout, groupCheckBoxParentLayout, groupName : str, checkBoxName : str, defaultState:bool, *ToggleShareDatas : ToggleShareData) -> FeatureShareGroup : 
        groupToggle = hlp.addCheckBox(checkBoxName,defaultState,groupCheckBoxParentLayout)
        groupLayout = hlp.addHidableGroup(
            groupParentLayout,
            groupCheckBoxParentLayout,
            groupName,
            groupToggle
        )
        # Use the regular GuiToggle as arg, create a Feature Toggle
        featureGroupToggles = FeatureShareGroup(
            groupToggle,
            functionWrappers=hlp.strListShareFactory(
                groupToggle, 
                *[Container_FeatureShareToggle_FunctionWrapperList(self.__addExtraFeatureShare_subCheckbox(data.name, data.val, data.defaultValue, groupLayout,requirement=data.requirement ), data.functionWrappers) for data in ToggleShareDatas]),
            featureName=groupName
        )
        self.extraFeaturesShared.append(featureGroupToggles)
        return featureGroupToggles        


    #Properties 
    props :list = field(default_factory=list)
    def addProp_checkbox(self, label:str, cmakePropName:str,cmakePropValue:bool, parentLayout) -> PropToggle:
        datToggle = hlp.addProp_CheckBox(label,cmakePropValue,parentLayout)
        datToggle.cmake_propName = cmakePropName        
        datToggle.setValue(cmakePropValue)
        self.props.append(datToggle)
        return datToggle

    def addProp_combobox_list(self, label:str, cmakePropName:str,cmakePropValues:list, defaultChoice:int, parentLayout) -> GuiDataComboBox:
        datComboboxList = hlp.addComboBox_list(label,cmakePropValues,parentLayout)
        datComboboxList.cmake_propName = cmakePropName
        # datToggle.widget.setState(cmakePropValue)
        
        datComboboxList.setValue(defaultChoice)
        self.props.append(datComboboxList)
    
    def addCmakeCppVarHeader(self, parentLayout):
        layout_headerTop  = hlp.createQHBoxLayout()
        layout_headerInput  = hlp.createQHBoxLayout()
        
        nameTitle  = hlp.createLabel("Variable Name")
        valueTitle = hlp.createLabel("Value")
        dummy = hlp.createLabel("") # Easy way to add spacing

        layout_headerTop.addWidget(nameTitle)
        layout_headerTop.addWidget(valueTitle)
        layout_headerTop.addWidget(dummy)

        input = CmakeCppVar_inputWidget("", str(""))

        layout_headerInput.addWidget(input.nameWidget)
        layout_headerInput.addWidget(input.valWidget)    

        addCmakeCppVarButton = hlp.addButton("Add/Edit", layout_headerInput)
        addCmakeCppVarButton.clicked.connect(lambda: self.addCmakeToCppVar(input.getVariable()[0],input.getVariable()[1], parentLayout))

        parentLayout.addLayout(layout_headerTop)
        parentLayout.addLayout(layout_headerInput)

    def addCmakeToCppVar(self, name : str, val, parentLayout ):
        
        if name == "" or str(val) == "": 
            return

        if name not in self.cmakeToCppVars:
            cmakeCppvar = CmakeCppVarWidget(name, str(val))
            newLayout = hlp.createQHBoxLayout()

            newLayout.addWidget(cmakeCppvar.nameWidget)
            newLayout.addWidget(cmakeCppvar.valWidget)

            remButton = hlp.addButton("-", newLayout)
            remButton.clicked.connect(lambda: self.remCmakeToCppVar(cmakeCppvar, remButton, newLayout))
            
            parentLayout.addLayout(newLayout)
            self.cmakeToCppVars[name] = cmakeCppvar
        else: 
            self.cmakeToCppVars[name].valWidget.setText(str(val))

    def remCmakeToCppVar(self, cmakeCppvar : CmakeCppVarWidget, remButton, layout):        
        self.cmakeToCppVars.pop(cmakeCppvar.nameWidget.text())
        layout.removeWidget(cmakeCppvar.nameWidget)
        layout.removeWidget(cmakeCppvar.valWidget)
        layout.removeWidget(remButton)


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
