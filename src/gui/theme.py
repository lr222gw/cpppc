from typing import Optional
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QColor

def getCol(c: QColor)->str:
    return "rgba"+c.getRgb().__str__()

class LabelLink(QLabel):
    def setLink(self,varname:str,linkText:str, textBefore: Optional[str] = None,textAfter: Optional[str] = None, objName : Optional[str]=None):
        def use(t :Optional[str]) -> str:
            return t if t != None else ''
                
        self.setText(f"{use(textBefore)} <a href=\"{varname}\" >{linkText}</a>  {use(textAfter)}")
        if objName != None:
            self.setObjectName(objName)
