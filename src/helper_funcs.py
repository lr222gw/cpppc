from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout


def addButton(text:str, layout:QVBoxLayout) -> QPushButton:
    newButton = QPushButton(text)
    layout.addWidget(newButton)
    return newButton

