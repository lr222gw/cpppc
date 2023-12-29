from PyQt5.QtWidgets import QLabel, QWidget
from dataclasses import dataclass

# NOTE: Class may be skipped if it remains this empty
@dataclass
class GuiData:
    widget: QWidget    

@dataclass
class GuiDataToggle:
    widget: QWidget    
    def toggle(self):
        self.widget.setCheckState(not self.widget.isChecked())
    def getState(self):        
        return self.widget.isChecked()