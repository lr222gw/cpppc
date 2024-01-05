from dataclasses import dataclass
from PyQt5.QtWidgets import *

@dataclass
class CMakeVersionData:
    major: QSpinBox
    def get_major(self) ->int:
        return self.major.value()

    minor: QSpinBox
    def get_minor(self) ->int:
        return self.minor.value()

    patch: QSpinBox
    def get_patch(self) ->int:
        return self.patch.value()

    def __init__(self, major:QSpinBox,minor:QSpinBox,patch:QSpinBox):
        self.major = major 
        self.minor = minor 
        self.patch = patch

    
    