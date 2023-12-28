from .structs import GuiData as d
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QSpinBox, QFormLayout, QTextEdit, QCheckBox ,QVBoxLayout


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

def addCheckBox(fieldName:str, defaultValue :bool, parentLayout) -> d.GuiData:
    
    # Create Label, input field widgets
    newCheckBox=QCheckBox(text=fieldName)    
    newCheckBox.setCheckState(defaultValue)
    newCheckBox.setTristate(False)
    # Append widgets to parent layout
    parentLayout.addWidget(newCheckBox)

    return d.GuiData(newCheckBox)    

def addCmakeVersionBox(fieldName:str, version:QSpinBox, parentLayout) -> d.GuiData:
    
    # Create Label, input field widgets
    newFieldLabel=QLabel(text=fieldName)
    # newSpinBox=QSpinBox()
    # newSpinBox.setValue(version)

    newLayout = QFormLayout()
    
    newLayout.addWidget(newFieldLabel)
    # newLayout.addWidget(newSpinBox)
    newLayout.addWidget(version)

    # Append widgets to parent layout    
    parentLayout.addLayout(newLayout)
    

    return d.GuiData(version)    