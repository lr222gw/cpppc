from typing import Callable
from .structs.GuiData import *
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QSpinBox, QFormLayout, QTextEdit, QCheckBox , QComboBox, QHBoxLayout,QFrame
from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *


def addButton(text:str, layout) -> QPushButton:
    newButton = QPushButton(text)
    layout.addWidget(newButton)
    return newButton

def addButton_gridLayout(text:str, gridLayout : QGridLayout, gridRow : int, gridColumn : int) -> QPushButton:
    newButton = QPushButton(text)
    gridLayout.addWidget(newButton, gridRow, gridColumn)
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

def placeTextField(textDat:GuiData[QLineEdit],label:QLabel, fieldName:str,placeholder:str, parentLayout):
    
    label.setText(fieldName)    
    textDat.widget.setPlaceholderText(placeholder)

    # Append widgets to parent layout
    parentLayout.addWidget(label)
    parentLayout.addWidget(textDat.widget)    

def addTextBoxField(fieldName:str, parentLayout, height:Optional[int]=50) -> GuiData:
    
    # Create Label, input field widgets
    newFieldLabel=QLabel(text=fieldName)
    newLineEdit=QTextEdit()
    newLineEdit.setFixedHeight(height) # type: ignore : has default value

    # Append widgets to parent layout
    parentLayout.addWidget(newFieldLabel)
    parentLayout.addWidget(newLineEdit)

    return GuiData(newLineEdit)

def placeTextBoxField(textDat:GuiData[QTextEdit],label:QLabel, fieldName:str,placeholder:str, parentLayout, height:Optional[int]=50):
    
    # Create Label, input field widgets
    label.setText(fieldName)
    textDat.widget.setFixedHeight(height) # type: ignore : has default value
    textDat.widget.setPlaceholderText(placeholder)

    # Append widgets to parent layout
    parentLayout.addWidget(label)
    parentLayout.addWidget(textDat.widget)


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
    newCheckBox.setCheckState(Qt.CheckState.Checked if defaultValue else  Qt.CheckState.Unchecked)
    newCheckBox.setTristate(False)
    # Append widgets to parent layout
    parentLayout.addWidget(newCheckBox)

    return GuiDataToggle(newCheckBox)   


def addProp_CheckBox(fieldName:str, defaultValue :bool, parentLayout) -> PropToggle:
    
    # Create Label, input field widgets
    newCheckBox=QCheckBox(text=fieldName)    
    newCheckBox.setCheckState(Qt.CheckState.Checked if defaultValue else  Qt.CheckState.Unchecked)
    newCheckBox.setTristate(False)
    # Append widgets to parent layout
    parentLayout.addWidget(newCheckBox)

    return PropToggle(newCheckBox)       

def addFeature_CheckBox(fieldName:str,value : str, defaultValue :bool, parentLayout) -> FeatureToggle:
    
    # Create Label, input field widgets
    newCheckBox=QCheckBox(text=fieldName)    
    newCheckBox.setCheckState(Qt.CheckState.Checked if defaultValue else  Qt.CheckState.Unchecked)
    newCheckBox.setTristate(False)
    # Append widgets to parent layout
    parentLayout.addWidget(newCheckBox)

    return FeatureToggle(newCheckBox,value)

def addFeatureShare_CheckBox(fieldName:str,value : str, defaultValue :bool, parentLayout) -> FeatureShareToggle:
    
    # Create Label, input field widgets
    newCheckBox=QCheckBox(text=fieldName)    
    newCheckBox.setCheckState(Qt.CheckState.Checked if defaultValue else  Qt.CheckState.Unchecked)
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

    funcCallDictionary :dict[Callable[...,None], list[FeatureShareToggle], ] = dict()
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
def lambdaHelper(toggles, parentCheckbox)->tuple[str, ...]:
    valueList :list[str] = list()
    for toggle in toggles:
        if toggle.getState() and parentCheckbox.getState():
            valueList.append(toggle.getValue())
            if toggle.requirement != None:
                toggle.requirement()
    
    a = tuple(valueList)
    return a

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
    newCheckBox.setCheckState(Qt.CheckState.Checked if defaultValue else  Qt.CheckState.Unchecked)
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
    checkbox :GuiDataToggle,
    minWdith: Optional[int] = None,
    minHeight:Optional[int] = None
) -> QVBoxLayout:
    minWdith  = minWdith  or 400 #Default values
    minHeight = minHeight or 0   #Default values

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
    frame_layout.setStretch(0, 1)
    frame_layout.setStretch(1, 1)

    # Add Checkbox to the provided Layout, used to toggle if hidden
    checkboxParentLayout.addWidget(checkbox.widget)

    # Add the frame Widget to the parent Layout to be displayed
    parentLayout.addWidget(frame_widget)    

    # Wrap the group_layout in a scroll area
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(group_widget)
    
    scroll_area.setMinimumSize(
        minWdith,   
        minHeight)  
    

    # Add the scroll area to the frame layout to make the group_layout scrollable
    frame_layout.addWidget(scroll_area)

    # Set Frame visible based on initial value of checkbox 
    # showHideFrame(frame_widget, checkbox.getState())    
    toggleHideShow_updGeoemtry(frame_widget, checkbox, scroll_area)    

    # Add checkbox toggle to frame    
    checkbox.registerConnection(
        # lambda: showHideFrame(frame_widget, checkbox.getState())
        lambda: toggleHideShow_updGeoemtry(frame_widget, checkbox, scroll_area)
    )   
    
    return group_layout

def variadicArgumentValidator(expectedNrOfArgs: int, *args):
    if len(args) != expectedNrOfArgs:
        errMsg = "Function not design to take anything but "+str(expectedNrOfArgs)+" variadic arguments, got "+str(len(args))+"\n"
        errMsg += "\t"+"\n\t".join(map(str, args) )
        terminate(errMsg)

def toggleHideShow_updGeoemtry(frame_widget, checkbox,scroll_area):    
    showHideFrame(frame_widget, checkbox.getState())
    scroll_area.updateGeometry()
   
def showHideFrame(frame :QFrame, condition:bool):    
    if condition:
        frame.show()
    else: 
        frame.hide()

def addFloatingWindow(
    parentLayout,
    groupTitle:str
) -> tuple[QVBoxLayout, QGroupBox]:

    # Create A frame, needed to make the layout/content collapsable
    frame_widget = QFrame()
    frame_widget.setWindowTitle(groupTitle)

    # Create new Layout for collapsable content, assign to frame widget
    frame_layout = QVBoxLayout()
    frame_widget.setLayout(frame_layout)
    frame_widget.resize(800,500)
    
    # Create A Group
    group_widget = QGroupBox(title=groupTitle)

    # new Layout for button and collapsable content, assign to group widget
    group_layout = QVBoxLayout()
    group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    group_widget.setLayout(group_layout)

    # Assign the group widget to the frames layout
    frame_layout.addWidget(group_widget)
    frame_layout.setStretch(0, 1)
    frame_layout.setStretch(1, 1)

    # Add the frame Widget to the parent Layout to be displayed
    parentLayout.addWidget(frame_widget)    

    frame_widget.show()

    # Wrap the group_layout in a scroll area
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(group_widget)
    
    scroll_area.setMinimumSize(245,0)

    # Add the scroll area to the frame layout to make the group_layout scrollable
    frame_layout.addWidget(scroll_area)

    return group_layout,group_widget
