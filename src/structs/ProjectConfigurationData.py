from typing import Tuple
from dataclasses import dataclass, field
from typing import Callable
from .CMakeVersionData import CMakeVersionData
from .GuiData import *
from .. import helper_funcs as hlp
from .CMakeCommands import *
from PyQt5.QtWidgets import *

@dataclass
class ProjectConfigurationData:     

    projectName :       GuiData
    def projectName_str(self) -> str:
        return self.projectName.widget.text()

    projectTargetDir :  GuiData
    def projectTargetDir_str(self) -> str:
        return self.projectTargetDir.widget.text()

    projectExecName :   GuiData
    def projectExecName_str(self) -> str:
        return self.projectExecName.widget.text()

    projectDesc :       GuiData
    def projectDesc_str(self) -> str:
        return self.projectDesc.widget.toPlainText()

    entryPointFile :   GuiData 
    def entryPointFile_str(self) -> str:
        return self.entryPointFile.widget.text()

    overwriteProjectTargetDir : GuiDataToggle

    #TODO: put inside a vector, enable user to use multiple programs...
    useProgram_ccache : GuiDataToggle

    useMeasureCompiletime : GuiDataToggle

    useCmakeCppBridge : GuiDataToggle

    cmakeToCppVars : dict 
    
    cmakeVersionData:  CMakeVersionData

    #Properties 
    props :list

    guiToggles          :list[GuiDataToggle] 
    extraFeatures       :list[FeatureGroup | FeatureToggle] 
    extraFeaturesShared :list[FeatureShareGroup | FeatureShareToggle]
    
    linkLibs_dict  : dict[str, library_inputWidget]
    #Todo: Use Dictionarys rather than lists...
    publicLinkLibs :list 
    privateLinkLibs:list 

    def __init__(self):
        self.projectName : GuiData                          = GuiData()
        self.projectTargetDir : GuiData                     = GuiData()
        self.projectExecName : GuiData                      = GuiData()
        self.projectDesc : GuiData                          = GuiData()
        self.entryPointFile : GuiData                       = GuiData()
        self.overwriteProjectTargetDir : GuiDataToggle      = GuiDataToggle()
        self.useProgram_ccache : GuiDataToggle              = GuiDataToggle()
        self.useMeasureCompiletime : GuiDataToggle          = GuiDataToggle()
        self.useCmakeCppBridge : GuiDataToggle              = GuiDataToggle()
        self.cmakeToCppVars : dict                          = dict()
        self.linkLibs_dict : dict[str, library_inputWidget] = dict[str, library_inputWidget]()
        self.props                                          = list()
        self.guiToggles          :list[GuiDataToggle]        = list[GuiDataToggle]()        
        self.extraFeatures       :list[FeatureGroup      | FeatureToggle]        = list[FeatureGroup      | FeatureToggle]()
        self.extraFeaturesShared :list[FeatureShareGroup | FeatureShareToggle]   = list[FeatureShareGroup | FeatureShareToggle]()
        #Todo: Use Dictionarys rather than lists...
        self.cmakeVersionData:  CMakeVersionData = CMakeVersionData()
        self.publicLinkLibs :list = list()
        self.privateLinkLibs:list = list()

    def initExtraFeatures(self):
        self.__initExtraFeature()
        self.__initExtraFeatureShared()
        self.__initGuiToggleRequirments()
    def __initExtraFeature(self):
        for feature in self.extraFeatures:
            feature.functionWrapper()
    def __initExtraFeatureShared(self):
        for feature in self.extraFeaturesShared:
            for functionWrapper in feature.functionWrappers:
                functionWrapper()

    def __initGuiToggleRequirments(self):
        for toggle in self.guiToggles:
            if(toggle.getState() and toggle.requirement != None):
                toggle.requirement()

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


    def addExtraFeatureGroup_UserInputs(self, groupParentLayout, groupCheckBoxParentLayout, groupName : str, checkBoxName : str, defaultState:bool, func:Callable[[QGridLayout,Input],None], *userInputHeaders : Input, requirement:Optional[Callable] = None) -> GuiDataToggle: 
        groupToggle = hlp.addCheckBox(checkBoxName,defaultState,groupCheckBoxParentLayout)
        groupLayout = hlp.addHidableGroup(
            groupParentLayout,
            groupCheckBoxParentLayout,
            groupName,
            groupToggle
        )
                
        self.addUserInput(groupLayout, func,*userInputHeaders)
        groupToggle.requirement = requirement
        self.guiToggles.append(groupToggle)        

        return groupToggle
    
    def addProp_checkbox(self, label:str, cmakePropName:str,cmakePropValue:bool, parentLayout) -> PropToggle:
        datToggle = hlp.addProp_CheckBox(label,cmakePropValue,parentLayout)
        datToggle.cmake_propName = cmakePropName        
        datToggle.setValue(cmakePropValue)
        self.props.append(datToggle)
        return datToggle

    def addProp_combobox_list(self, label:str, cmakePropName:str,cmakePropValues:list, defaultChoice:int, parentLayout):
        datComboboxList = hlp.addComboBox_list(label,cmakePropValues,parentLayout)
        datComboboxList.cmake_propName = cmakePropName
        # datToggle.widget.setState(cmakePropValue)
        
        datComboboxList.setValue(defaultChoice)
        self.props.append(datComboboxList)

    def addUserInput(self, parentLayout, func:Callable[[QGridLayout,Input],None], *headers : Input):
        layout_grid = QGridLayout()
        layout_grid.setAlignment(combine_alignment_flags(Qt.AlignmentFlag.AlignTop, Qt.AlignmentFlag.AlignLeading))
        
        columnCounter = 0
        for header in headers:
            layout_grid.addWidget(header.label.labelView,0,columnCounter)            
            layout_grid.setAlignment(header.label.labelView,combine_alignment_flags(Qt.AlignmentFlag.AlignBottom, Qt.AlignmentFlag.AlignLeft) )
            
            columnCounter += 1
        
        columnCounter = 0
        for header in headers:
            layout_grid.addWidget(header.input.getWidget(), 1, columnCounter)
            columnCounter += 1
        
        newButton = QPushButton("Add/Edit")
        layout_grid.addWidget(newButton, 1, columnCounter)
        newButton.clicked.connect(lambda: func(layout_grid,*headers))
        
        parentLayout.addLayout(layout_grid)

    def addCmakeToCppVar(self, gridLayout: QGridLayout, *args: Input ):
        hlp.variadicArgumentValidator(2, *args)
        name  = args[0].getInputText()
        value = args[1].getInputText()
        if name == "" or value == "":
            print("Nothing to add!") 
            return            

        if name not in self.cmakeToCppVars:
            cmakeCppvar = CmakeCppVar_inputWidget(name, str(value))           
            row = gridLayout.rowCount() +1

            gridLayout.addWidget(cmakeCppvar.nameWidget, row, 0)
            gridLayout.addWidget(cmakeCppvar.valWidget, row, 1)            

            remButton = hlp.addButton_gridLayout("-", gridLayout, row, 2)
            remButton.clicked.connect(lambda: self.remCmakeToCppVar(cmakeCppvar, remButton, gridLayout))            
            
            self.cmakeToCppVars[name] = cmakeCppvar
        else: 
            self.cmakeToCppVars[name].valWidget.setText(str(value))

    def remCmakeToCppVar(self, cmakeCppVar: CmakeCppVar_inputWidget, remButton, layout : QGridLayout):    
        cmakeCppVar.nameWidget.deleteLater()
        cmakeCppVar.valWidget.deleteLater()
        remButton.deleteLater()
        self.cmakeToCppVars.pop(cmakeCppVar.nameWidget.text())

    def addLibraryComponent(self, gridLayout: QGridLayout, *args: Input):
        hlp.variadicArgumentValidator(3, *args)
            
        publicUserInput : Input= args[0]
        name_str  = args[1].getInputText()
        value_str = args[2].getInputText()
        if name_str == "" or value_str == "":
            print("Nothing to add!") 
            return    

        if name_str not in self.linkLibs_dict:
            libVar = library_inputWidget(name_str, str(value_str), publicUserInput.input.getState())           
            row = gridLayout.rowCount() +1
            
            gridLayout.addWidget(libVar.public.widget, row, 0)
            gridLayout.addWidget(libVar.nameWidget, row, 1)
            gridLayout.addWidget(libVar.valWidget, row, 2)

            remButton = hlp.addButton_gridLayout("-", gridLayout, row, 3)
            remButton.clicked.connect(lambda: self.remLibraryComponent(libVar, remButton, gridLayout))            
        
            self.linkLibs_dict[name_str] = libVar
        else:
            self.linkLibs_dict[name_str].valWidget.setText(str(value_str))
            self.linkLibs_dict[name_str].public.setState(publicUserInput.input.getState())

    def remLibraryComponent(self, libItem: library_inputWidget, remButton, layout : QGridLayout):    
        libItem.nameWidget.deleteLater()
        libItem.valWidget.deleteLater()
        libItem.public.widget.deleteLater()
        remButton.deleteLater()
        self.linkLibs_dict.pop(libItem.nameWidget.text())

    def getTargetPath(self) -> str:
        path = self.projectTargetDir.widget.text() + "/" + self.projectName.widget.text()
        return path    
    def toString(self):
        print(f"ProjectName:{self.projectName.widget.text()}")
        print(f"projectTargetDir:{self.projectTargetDir.widget.text()}")
        print(f"projectExecName:{self.projectExecName.widget.text()}")
        print(f"projectDesc:{self.projectDesc.widget.toPlainText()}")
        print(f"cmakeVersionData.major:{self.cmakeVersionData.get_major()}")
        print(f"cmakeVersionData.minor:{self.cmakeVersionData.get_minor()}")
        print(f"cmakeVersionData.patch:{self.cmakeVersionData.get_patch()}")
