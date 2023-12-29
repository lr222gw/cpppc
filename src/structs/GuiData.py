from PyQt5.QtWidgets import QLabel, QWidget, QComboBox
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
