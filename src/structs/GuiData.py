from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Tuple, TypeVar,Optional
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
import math
from src.structs.GenericTypeValueSetterMetaClass import GenericTypeValueSetterMetaClass
from ..dev.Terminate import terminate

T = TypeVar("T")
@dataclass
class GuiData(Generic[T], metaclass=GenericTypeValueSetterMetaClass):
    widget: T 

    def __initT(self, t):
        self.widget = t()

    def registerConnection(self, func : Callable):
        if isinstance(self.widget,QWidget):
            self.widget.clicked.connect(func)

    def getWidget(self)->T:
        return self.widget

@dataclass
class GuiDataToggle(GuiData[QCheckBox], classType=QCheckBox, superRoot=GuiData):
    def __init__(self, widget : Optional[QCheckBox] = None, requirement : Optional[Callable] = None ):
        self.widget = widget if widget != None else QCheckBox()
        self.requirement = requirement        

    def toggle(self):
        self.widget.setCheckState(not self.widget.isChecked())
    def setState(self, value):
        self.widget.setChecked(value)            
    def getState(self):        
        return self.widget.isChecked()

@dataclass
class GuiDataComboBox(GuiData[QComboBox], classType=QComboBox, superRoot=GuiData):
    def getValue(self):        
        return self.widget.currentText()
    
@dataclass
class GuiDataLineEdit(GuiData[QLineEdit], classType=QLineEdit, superRoot=GuiData):
    def __init__(self, widget : Optional[QLineEdit] = None, requirement : Optional[Callable] = None ):
        self.widget = widget if widget != None else QLineEdit()
        self.requirement = requirement        
    
    def setText(self, value):
        self.widget.setText(value)            
    def getText(self):        
        return self.widget.text()

@dataclass
class Prop():    
    cmake_propName : str = "<MISSING NAME>"
    @abstractmethod
    def setValue(self, value):
        pass
    @abstractmethod
    def getValue(self) -> Any:
        pass

@dataclass
class PropToggle(Prop, GuiDataToggle):
    def setValue(self, value):
        self.widget.setChecked(value)        

    def getValue(self) -> str:
        return "ON" if self.widget.isChecked() else "OFF"

@dataclass
class PropComboBox(Prop, GuiDataComboBox):
    def setValue(self, value):
        self.widget.setCurrentIndex(value)

    def getValue(self) -> str:
        return self.widget.currentText()


def __defaultFunc__(*args):
    terminate("Feature function not implemented")

@dataclass
class FunctionWrapper(): 
    func : Callable[..., None]  = field(default=lambda *args:None)
    arg  : Callable[[],Tuple]  = field(default=lambda:())
        
    def __call__(self):
        self.func(*self.arg())

@dataclass
# class Feature(AbstractGenericTypeValueSetterMetaClass):    
class Feature():    
    value : str
    functionWrapper : FunctionWrapper = field(default_factory=FunctionWrapper)
    featureName : str = "<MISSING NAME>"
    @abstractmethod
    def setValue(self, value):
        pass
    @abstractmethod
    def getValue(self) -> Any:
        pass

@dataclass
# class FeatureShare(AbstractGenericTypeValueSetterMetaClass):    
class FeatureShare():    
    value : str
    functionWrappers : list[FunctionWrapper] = field(default_factory=list)
    featureName : str = "<MISSING NAME>"
    @abstractmethod
    def setValue(self, value):
        pass
    @abstractmethod
    def getValue(self) -> Any:
        pass

@dataclass
class FeatureToggle(Feature, GuiDataToggle):
    
    def setValue(self, value):
        self.value = value    
    def getValue(self) -> str:
        return self.value

@dataclass
class FeatureShareToggle(FeatureShare, GuiDataToggle):
    
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
    def getValue(self) -> Any:
        pass         

@dataclass
class FeatureShareGroup(GuiDataToggle):
    functionWrappers : list[FunctionWrapper] = field(default_factory=list[FunctionWrapper])
    featureName : str = "<MISSING NAME>"
    @abstractmethod
    def setValue(self, value):
        pass
    @abstractmethod
    def getValue(self) -> Any:
        pass          

@dataclass
class ToggleData():
    name : str
    val  : str 
    defaultValue : bool
    requirement : Optional[Callable]
    def __init__(self,name,val,defaultValue, requirement: Optional[Callable] = None):
        self.name = name
        self.val = val
        self.defaultValue = defaultValue
        self.requirement = requirement

@dataclass
class ToggleShareData(ToggleData):
    name : str
    val  : str 
    defaultValue : bool
    requirement : Optional[Callable]
    functionWrappers : list[FunctionWrapper] = field(default_factory=list[FunctionWrapper])
    def __init__(self,name,val,defaultValue, *args, requirement: Optional[Callable] = None):
        self.name = name
        self.val = val
        self.defaultValue = defaultValue
        self.functionWrappers = list(args)
        self.requirement = requirement

@dataclass
class InputWidget():    
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
class CmakeCppVar_inputWidget(InputWidget):
    def __init__(self, name:str, val):
        super().__init__(name, val)
        
        self.nameWidget.setDisabled(True)
        self.valWidget.setDisabled(True)

    
@dataclass
class library_inputWidget(InputWidget):
    public: GuiDataToggle
    def __init__(self, name : str, val : str, public: bool):
        super().__init__(name, val)
        self.public = GuiDataToggle(QCheckBox())
        self.public.setState(public)

    def setPublicVisibilitySpecifier(self, isPublic : bool):
        self.public.setState(isPublic)

    def getPublicVisibilitySpecifier(self) -> bool:
        return self.public.getState()
    pass

@dataclass
class Label():
    
    labelText: str
    labelView: QGraphicsView
    labelScene: QGraphicsScene
    text_item: QGraphicsSimpleTextItem
    layout: QVBoxLayout

    @property
    def label(self)->QLabel:...
    @label.setter
    def label(self, value):...

    

    def __init__(self, labelName: str, rot: int = 0):
        self.labelText = labelName
        
        self.label = QLabel(self.labelText)
        

        self.labelView = QGraphicsView(self.label)
        self.labelScene = QGraphicsScene(self.label)

        self.text_item = QGraphicsSimpleTextItem(self.labelText)                
        self.text_item.setBrush(Qt.GlobalColor.white)

        self.labelView.setMaximumHeight(int(self.text_item.boundingRect().height()))

        self.labelView.setScene(self.labelScene)

        self.labelView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.labelView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.labelView.setFrameShape(QFrame.Shape.NoFrame)
        self.labelView.setStyleSheet("background: transparent")
        
        self.labelView.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)        
                
        self.labelScene.addItem(self.text_item)
                
        if(rot != 0):
            self.setRotation(rot)

    def setText(self, text: str):
        self.labelText = text
        self.label.setText(self.labelText)
        self.text_item.setText(self.labelText)
        
    def getText(self) -> str:
        return self.labelText

    def setRotation(self, rot : int):
        padding = 5
        textHeight = self.text_item.boundingRect().height()
        self.labelScene.sceneRect()
        textWidth  = self.text_item.boundingRect().width()

        self.labelView.setMaximumHeight(int(textWidth))
        self.labelView.setMaximumWidth(int(textHeight))
        self.text_item.setTransformOriginPoint(self.text_item.boundingRect().bottom(),self.text_item.boundingRect().center().x())
        self.text_item.setRotation(rot)        
        self.text_item.update()
        self.labelScene.update()

T = TypeVar('T')
@dataclass
class Input(GuiData[T], Generic[T]):
    label : Label
    input : T = T  # type: ignore

    def __initT(self, t):
        self.input = t

    def initT(self, t):
        self.input = t

    def __init__(self, labelStr : str, defaultState: bool = True,  rotation : Optional[int] = 0):        
        self.label = Label(labelStr, rotation) # type: ignore will never be `None`...
        # self.input :T = T_instance

    @abstractmethod
    def setVariable(self, name:str, value):pass             

    @abstractmethod
    def getVariable(self) -> tuple:pass     

    @abstractmethod
    def getLabelText(self) -> str:pass

    @abstractmethod
    def getInputText(self) -> Any:pass

@dataclass
# class UserInput(Input[GuiDataLineEdit], classType=GuiDataLineEdit):
# class UserInput(Input):
class UserInput(Input[GuiDataLineEdit], classType=GuiDataLineEdit, superRoot=Input):

    def __init__(self, labelStr : str, rotation : Optional[int] = 0):        
        self.label = Label(labelStr, rotation) # type: ignore will never be `None`...
        # self.input :GuiDataLineEdit = GuiDataLineEdit()
                
    def setVariable(self, name:str, value):        
        self.label.setText(name)
        self.input.setText(str(value))

    def getVariable(self) -> tuple:
        return (self.label.labelText, self.input.getText())

    def getLabelText(self) -> str:
        return self.label.getText()
    def getInputText(self) -> str:
        return self.input.getText()
    
    def __str__(self):
        return "UserInput:["+self.label.getText()+"]"

class UserInput_checkbox(Input[GuiDataToggle], classType=GuiDataToggle, superRoot=Input):

    def __init__(self, labelStr : str, defaultVal:bool,rotation : Optional[int] = 0):
        self.label = Label(labelStr, rotation)# type: ignore will never be `None`...
        self.input.setState(defaultVal)

    def setVariable(self, name:str, value : bool):
        self.label.setText(name)
        self.input.setState(value)

    def getVariable(self) -> tuple:
        return (self.label.getText(), self.input.getState())

    def getLabelText(self) -> str:
        return self.label.getText()
    def getInputText(self) -> bool:
        return self.input.getState()
    
    def __str__(self):
        return "UserInput:["+self.label.getText()+"]"    


@dataclass
class Container_FeatureShareToggle_FunctionWrapperList():
    featureShareToggle : FeatureShareToggle = field(default_factory=FeatureShareToggle)
    functions : list[Callable]  = field(default_factory=list[Callable])