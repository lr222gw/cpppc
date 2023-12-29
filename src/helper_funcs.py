from .structs import GuiData as d
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QSpinBox, QFormLayout, QTextEdit, QCheckBox , QComboBox, QHBoxLayout


def addButton(text:str, layout) -> QPushButton:
    newButton = QPushButton(text)
    layout.addWidget(newButton)
    return newButton

def addTextField(fieldName:str,placeholder:str, parentLayout) -> d.GuiData:
    
    # Create Label, input field widgets
    newFieldLabel=QLabel(text=fieldName)
    newLineEdit=QLineEdit()
    newLineEdit.setPlaceholderText(placeholder)

    # Append widgets to parent layout
    parentLayout.addWidget(newFieldLabel)
    parentLayout.addWidget(newLineEdit)

    return d.GuiData(newLineEdit)

def addTextBoxField(fieldName:str, parentLayout) -> d.GuiData:
    
    # Create Label, input field widgets
    newFieldLabel=QLabel(text=fieldName)
    newLineEdit=QTextEdit()

    # Append widgets to parent layout
    parentLayout.addWidget(newFieldLabel)
    parentLayout.addWidget(newLineEdit)

    return d.GuiData(newLineEdit)

def addSpinBox(fieldName:str, parentLayout) -> d.GuiData:
    
    # Create Label, input field widgets
    newFieldLabel=QLabel(text=fieldName)
    newSpinBox=QSpinBox()

    # Append widgets to parent layout
    parentLayout.addWidget(newFieldLabel)
    parentLayout.addWidget(newSpinBox)

    return d.GuiData(newSpinBox)

def addCheckBox(fieldName:str, defaultValue :bool, parentLayout) -> d.GuiDataToggle:
    
    # Create Label, input field widgets
    newCheckBox=QCheckBox(text=fieldName)    
    newCheckBox.setCheckState(defaultValue)
    newCheckBox.setTristate(False)
    # Append widgets to parent layout
    parentLayout.addWidget(newCheckBox)

    return d.GuiDataToggle(newCheckBox)    

def addCmakeVersionBox(fieldName:str, version:QSpinBox, parentLayout) -> d.GuiData:
    # Create Label, input field widgets
    newFieldLabel=QLabel(text=fieldName)
    newLayout = QFormLayout()
    
    newLayout.addWidget(newFieldLabel)
    # newLayout.addWidget(newSpinBox)
    newLayout.addWidget(version)

    # Append widgets to parent layout    
    parentLayout.addLayout(newLayout)
    

    return d.GuiData(version)    

def addCppLanguageStandardBox(fieldName:str, parentLayout ) -> d.GuiDataComboBox:    
    # Create Label, input field widgets
    newFieldLabel=QLabel(text=fieldName)
    version = QComboBox()
    newLayout = QHBoxLayout()

    cppLangStandards = [98,11,14,17,20,23,26]
    for standard in cppLangStandards:
        version.addItem(str(standard))

    # Append widgets to new layout, then to parent layout
    newLayout.addWidget(newFieldLabel)
    newLayout.addWidget(version)
    parentLayout.addRow(newLayout)    

    return d.GuiData(version)    