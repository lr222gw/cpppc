from dataclasses import dataclass
from PyQt5.QtWidgets import *

@dataclass
class CMakeVersionData:
    major: QSpinBox
    minor: QSpinBox
    patch: QSpinBox

    def __init__(self, major:int = 0,minor:int = 0,patch:int = 0):
        self.major = QSpinBox()
        self.major.setValue(major)
        self.minor = QSpinBox()
        self.minor.setValue(minor)
        self.patch = QSpinBox()
        self.patch.setValue(patch)

    def get_major(self) ->int:
        return self.major.value()

    def get_minor(self) ->int:
        return self.minor.value()

    def get_patch(self) ->int:
        return self.patch.value()


    
    