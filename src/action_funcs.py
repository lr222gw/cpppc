from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import *
from src.gui.theme import getCol
import src.gui.theme as theme

def warningPopup(msg :str):
    print(str.format("Error: {}", msg))
    
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Critical)

    error_box.setWindowTitle("Error")
    error_box.setText(msg)

    # Add a button to close the message box
    error_box.addButton(QMessageBox.Ok)

    error_box.exec_()