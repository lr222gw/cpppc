from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QLabel, QWidget, QComboBox, QCheckBox, QLineEdit
from dataclasses import dataclass, field
from typing import Callable, Tuple
from ..dev.Terminate import terminate

# NOTE: Class may be skipped if it remains this empty
@dataclass
class GuiData:
    widget: QWidget
    def registerConnection(self, func : Callable):
        self.widget.clicked.connect(func)

@dataclass
class GuiDataToggle(GuiData):
    widget: QCheckBox
    def toggle(self):
        self.widget.setCheckState(not self.widget.isChecked())
    def setState(self, value):
        self.widget.setChecked(value)            
    def getState(self):        
        return self.widget.isChecked()

@dataclass
class GuiDataComboBox(GuiData):
    widget: QComboBox
    def getValue(self):        
        return self.widget.currentText()

@dataclass
class CmakeCppVarWidget():    
    nameWidget: QLineEdit
    valWidget : QLineEdit
        
    def __init__(self, name:str, val):
        self.nameWidget = QLineEdit()
        self.valWidget  = QLineEdit()
        self.nameWidget.setText(name)
        self.valWidget.setText(str(val))    

        self.nameWidget.setDisabled(True)
        self.valWidget.setDisabled(True)

    def setVariable(self, name:str, value):
        self.nameWidget.setText(name)
        self.valWidget.setText(str(value))

    def getVariable(self) -> tuple:
        return (self.nameWidget.text(), self.valWidget.text())

@dataclass
class CmakeCppVar_inputWidget():    
    nameWidget: QLineEdit
    valWidget : QLineEdit
        
    def __init__(self, name:str, val):
        self.nameWidget = QLineEdit()
        self.valWidget  = QLineEdit()
        self.nameWidget.setText(name)
        self.valWidget.setText(str(val))    

    def setVariable(self, name:str, value):
        self.nameWidget.setText(name)
        self.valWidget.setText(str(value))

    def getVariable(self) -> tuple:
        return (self.nameWidget.text(), self.valWidget.text())

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

    def getValue(self) -> str:
        return "ON" if self.widget.isChecked() else "OFF"

@dataclass
class PropComboBox(Prop, GuiDataComboBox):
    def setValue(self, index):
        self.widget.setCurrentIndex(index)

    def getValue(self) -> str:
        return self.widget.currentText()


def __defaultFunc__(*args):
    terminate("Feature function not implemented")



@dataclass
class FunctionWrapper():
    func : Callable[..., None]  = field(default=lambda *args:())
    arg  : Callable[[],Tuple]  = field(default=lambda:())
        
    def __call__(self):
        self.func(*self.arg())

@dataclass
class Feature(ABC):    
    value : str
    functionWrapper : FunctionWrapper = field(default_factory=FunctionWrapper)
    featureName : str = "<MISSING NAME>"
    @abstractmethod
    def setValue(self, value):
        pass
    @abstractmethod
    def getValue(self) -> any:
        pass

@dataclass
class FeatureToggle(Feature, GuiDataToggle):
    
    def setValue(self, value):
        self.value = value    
    def getValue(self) -> str:
        return self.value

@dataclass
class FeatureGroup(GuiDataToggle):
    functionWrapper : FunctionWrapper = field(default_factory=FunctionWrapper)
    featureName : str = "<MISSING NAME>"
    @abstractmethod
    def setValue(self, value):
        pass
    @abstractmethod
    def getValue(self) -> any:
        pass        

@dataclass
class ToggleData():
    name : str
    val  : str 
    defaultValue : bool
