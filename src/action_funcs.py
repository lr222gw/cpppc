from .structs import GuiData as d
from .structs.ProjectConfigurationData import ProjectConfigurationData
from .structs.CppDataHelper import CppDataHelper
from . import cmake_helper as hlp_cmake
from PyQt5.QtWidgets import QMessageBox, QTextEdit
import os
from . import cmake_helper as cm_hlp
from .structs.CMakeData import *


# Testing access of input data
def test(guidata : d.GuiData):
    alert = QMessageBox(text= "User provided following input: "+guidata.widget.text() )
    alert.exec()

def cmakebuttontest():
    hlp_cmake.getCMakeVersion()

