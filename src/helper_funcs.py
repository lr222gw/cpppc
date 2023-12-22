from . import data_class as d
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout


def addButton(text:str, layout) -> QPushButton:
    newButton = QPushButton(text)
    layout.addWidget(newButton)
    return newButton

def addTextField(fieldName:str, parentLayout) -> d.GuiData:
    
    # Create Label, input field widgets
    newFieldLabel=QLabel(text=fieldName)
    newLineEdit=QLineEdit()

    # Append widgets to parent layout
    parentLayout.addWidget(newFieldLabel)
    parentLayout.addWidget(newLineEdit)

    return d.GuiData(newLineEdit)
