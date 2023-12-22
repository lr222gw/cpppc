from . import data_class as d
from PyQt5.QtWidgets import QMessageBox

# Testing access of input data
def test(guidata : d.GuiData):
    alert = QMessageBox(text= "User provided following input: "+guidata.widget.text() )
    alert.exec()


