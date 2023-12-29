from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QLabel, QWidget, QComboBox, QCheckBox
from dataclasses import dataclass

# NOTE: Class may be skipped if it remains this empty
@dataclass
class GuiData:
    widget: QWidget    

@dataclass
class GuiDataToggle:
    widget: QCheckBox
    def toggle(self):
        self.widget.setCheckState(not self.widget.isChecked())
    def getState(self):        
        return self.widget.isChecked()

@dataclass
class GuiDataComboBox:
    widget: QComboBox
    def getValue(self):        
        return self.widget.currentText()

@dataclass
class Prop(ABC):    
    cmake_propName : str = "<MISSING NAME>"
    @abstractmethod
    def setValue(self, value):
        pass
    @abstractmethod
    def getValue(self) -> any:
        pass

@dataclass
class PropToggle(Prop, GuiDataToggle):
    def setValue(self, value):
        self.widget.setChecked(value)        

    def getValue(self) -> bool:
        return "ON" if self.widget.isChecked() else "OFF"

@dataclass
class PropComboBox(Prop, GuiDataComboBox):
    def setValue(self, index):
        self.widget.setCurrentIndex(index)

    def getValue(self) -> str:
        return self.widget.currentText()