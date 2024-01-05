from typing import Callable
from .structs.GuiData import *
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QSpinBox, QFormLayout, QTextEdit, QCheckBox , QComboBox, QHBoxLayout,QFrame
from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *


def addButton(text:str, layout) -> QPushButton:
    newButton = QPushButton(text)
    layout.addWidget(newButton)
    return newButton

def addTextField(fieldName:str,placeholder:str, parentLayout) -> GuiData:
    
    # Create Label, input field widgets
    newFieldLabel=QLabel(text=fieldName)
    newLineEdit=QLineEdit()
    newLineEdit.setPlaceholderText(placeholder)

    # Append widgets to parent layout
    parentLayout.addWidget(newFieldLabel)
    parentLayout.addWidget(newLineEdit)

    return GuiData(newLineEdit)

def addTextBoxField(fieldName:str, parentLayout) -> GuiData:
    
    # Create Label, input field widgets
    newFieldLabel=QLabel(text=fieldName)
    newLineEdit=QTextEdit()

    # Append widgets to parent layout
    parentLayout.addWidget(newFieldLabel)
    parentLayout.addWidget(newLineEdit)

    return GuiData(newLineEdit)

def addSpinBox(fieldName:str, parentLayout) -> GuiData:
    
    # Create Label, input field widgets
    newFieldLabel=QLabel(text=fieldName)
    newSpinBox=QSpinBox()

    # Append widgets to parent layout
    parentLayout.addWidget(newFieldLabel)
    parentLayout.addWidget(newSpinBox)

    return GuiData(newSpinBox)

def addCheckBox(fieldName:str, defaultValue :bool, parentLayout) -> GuiDataToggle:
    
    # Create Label, input field widgets
    newCheckBox=QCheckBox(text=fieldName)    
    newCheckBox.setCheckState(defaultValue)
    newCheckBox.setTristate(False)
    # Append widgets to parent layout
    parentLayout.addWidget(newCheckBox)

    return GuiDataToggle(newCheckBox)   


def addProp_CheckBox(fieldName:str, defaultValue :bool, parentLayout) -> PropToggle:
    
    # Create Label, input field widgets
    newCheckBox=QCheckBox(text=fieldName)    
    newCheckBox.setCheckState(defaultValue)
    newCheckBox.setTristate(False)
    # Append widgets to parent layout
    parentLayout.addWidget(newCheckBox)

    return PropToggle(newCheckBox)       

def addFeature_CheckBox(fieldName:str,value : str, defaultValue :bool, parentLayout) -> FeatureToggle:
    
    # Create Label, input field widgets
    newCheckBox=QCheckBox(text=fieldName)    
    newCheckBox.setCheckState(defaultValue)
    newCheckBox.setTristate(False)
    # Append widgets to parent layout
    parentLayout.addWidget(newCheckBox)

    return FeatureToggle(newCheckBox,value)

def addFeatureShare_CheckBox(fieldName:str,value : str, defaultValue :bool, parentLayout) -> FeatureShareToggle:
    
    # Create Label, input field widgets
    newCheckBox=QCheckBox(text=fieldName)    
    newCheckBox.setCheckState(defaultValue)
    newCheckBox.setTristate(False)
    
    # Append widgets to parent layout
    parentLayout.addWidget(newCheckBox)

    return FeatureShareToggle(newCheckBox,value)        

def strListFactory(func :Callable, parentCheckbox : GuiDataToggle, *args) -> FunctionWrapper:

    funcWrapper = FunctionWrapper(
        func,
        lambda toggles=args, parentCheckbox=parentCheckbox : lambdaHelper(toggles,parentCheckbox)
    )
    
    return funcWrapper

def strListShareFactory(parentCheckbox : GuiDataToggle, *args : Container_FeatureShareToggle_FunctionWrapperList) -> list[FunctionWrapper]:

    funcCallDictionary :dict[list] = dict()
    # Prepare dictionary
    for toggleFuncPair in args:                        
        for func in toggleFuncPair.functions:
            if func not in funcCallDictionary.keys():
                funcCallDictionary.setdefault(func, [])
            funcCallDictionary[func].append(toggleFuncPair.featureShareToggle)

    functionWrapperList : list[FunctionWrapper] = []
    for (func, toggles) in funcCallDictionary.items():
        functionWrapperList.append(
            FunctionWrapper(
                func,
                lambda toggles=toggles, parentCheckbox=parentCheckbox : lambdaHelper(toggles,parentCheckbox)
            )
        )

    return functionWrapperList
def lambdaHelper(toggles, parentCheckbox)->list[str]:
    valueList = list()
    for toggle in toggles:
        if toggle.getState() and parentCheckbox.getState():
            valueList.append(toggle.getValue())
            if toggle.requirement != None:
                toggle.requirement()
    
    return valueList 

def addCmakeVersionBox(fieldName:str, version:QSpinBox, parentLayout) -> GuiData:
    # Create Label, input field widgets
    newFieldLabel=QLabel(text=fieldName)
    newLayout = QFormLayout()
    
    newLayout.addWidget(newFieldLabel)
    # newLayout.addWidget(newSpinBox)
    newLayout.addWidget(version)

    # Append widgets to parent layout    
    parentLayout.addLayout(newLayout)
    

    return GuiData(version)    

def addComboBox_list(fieldName:str, alternatives : list, parentLayout ) -> PropComboBox:    
    # Create Label, input field widgets
    newFieldLabel=QLabel(text=fieldName)
    version = QComboBox()
    newLayout = QHBoxLayout()

    for standard in alternatives:
        version.addItem(str(standard))

    # Append widgets to new layout, then to parent layout
    newLayout.addWidget(newFieldLabel)
    newLayout.addWidget(version)
    parentLayout.addRow(newLayout)    

    return PropComboBox(version)    

def createLabel(text) -> QLabel:
    newLabel = QLabel(text=text)
    return newLabel

def createQHBoxLayout() -> QHBoxLayout:
    newLayout = QHBoxLayout()
    return newLayout

def createCheckBox(fieldName:str, defaultValue :bool) -> PropToggle:        
    newCheckBox=QCheckBox(text=fieldName)    
    newCheckBox.setCheckState(defaultValue)
    newCheckBox.setTristate(False)

    return PropToggle(newCheckBox)    

def addHidableFrame(
    parentLayout,
    groupTitle:str,
    checkbox :PropToggle
) -> QVBoxLayout:
    # Create A Group
    group_widget = QGroupBox(title=groupTitle)

    # new Layout for button and collapsable content, assign to group widget
    group_layout = QVBoxLayout()
    group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    group_widget.setLayout(group_layout)

    # Add Checkbox to the groups Layout, used to toggle if hidden
    group_layout.addWidget(checkbox.widget)

    # Add the group Widget to the parent Layout to be displayed
    parentLayout.addWidget(group_widget)

    # Create A frame, needed to make the layout/content collapsable
    frame_widget = QFrame()

    # Create new Layout for collapsable content, assign to frame widget, then add frame widget to group layout
    frame_layout = QVBoxLayout()
    frame_widget.setLayout(frame_layout)
    group_layout.addWidget(frame_widget)

    # Set Frame visible based on initial value of checkbox 
    showHideFrame(frame_widget, checkbox.getState())    

    # Add checkbox toggle to frame    
    checkbox.registerConnection(
        lambda: showHideFrame(frame_widget, checkbox.getState())
    )   

    return frame_layout

def addHidableGroup(
    parentLayout,
    checkboxParentLayout,
    groupTitle:str,
    checkbox :GuiDataToggle
) -> QVBoxLayout:

    # Create A frame, needed to make the layout/content collapsable
    frame_widget = QFrame()

    # Create new Layout for collapsable content, assign to frame widget
    frame_layout = QVBoxLayout()
    frame_widget.setLayout(frame_layout)
    
    # Create A Group
    group_widget = QGroupBox(title=groupTitle)

    # new Layout for button and collapsable content, assign to group widget
    group_layout = QVBoxLayout()
    group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    group_widget.setLayout(group_layout)

    # Assign the group widget to the frames layout
    frame_layout.addWidget(group_widget)

    # Add Checkbox to the provided Layout, used to toggle if hidden
    checkboxParentLayout.addWidget(checkbox.widget)

    # Add the frame Widget to the parent Layout to be displayed
    parentLayout.addWidget(frame_widget)    

    # Set Frame visible based on initial value of checkbox 
    showHideFrame(frame_widget, checkbox.getState())    

    # Add checkbox toggle to frame    
    checkbox.registerConnection(
        lambda: showHideFrame(frame_widget, checkbox.getState())
    )   

    return group_layout
   
def showHideFrame(frame :QFrame, condition:bool):    
    if condition:
        frame.show()
    else: 
        frame.hide()