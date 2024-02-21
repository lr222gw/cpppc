from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *

def getCol(c: QColor)->str:
    return "rgba"+c.getRgb().__str__()


def initColorTheme(app : QApplication):

    def getCol(c: QColor)->str:
        return "rgba"+c.getRgb().__str__()
    
    palette = app.palette()
            
    dark_color                  = QColor(37, 42, 52)
    widgetBackground_color      = QColor(24, 25, 29) 
    frametitleBack_color        = QColor(24, 25, 29, 75) 
    frametitleBackBorder_color  = QColor(24, 25, 29, 135) 
    text_color                  = QColor(234, 234, 234)
    highlighttext_color         = QColor(234, 234, 0)
    placeHoldertext_color       = QColor(105, 105, 105)
    button_color                = QColor(8, 217, 214)
    labelLink_color             = button_color
    checkboxBorder_color        = QColor(255,4,255, 95)
    groupBorder_color           = QColor(8, 217, 214, 250)
    subGroupBorder_color        = QColor(8, 217, 214, 75)
    textButton_color            = QColor(0, 0, 0)
    textCheckbox_color          = QColor(8, 217, 214)
    textLink_color              = QColor(8, 217, 214)
    scrollbar_color             = QColor(8, 217, 214, 150)
    scrollbarBackground_color   = frametitleBackBorder_color
    transparent_color           = QColor(255, 255, 255, 0)

    palette.setColor(app.palette().Window, dark_color)
    palette.setColor(app.palette().WindowText, text_color)
    palette.setColor(app.palette().Button, button_color)
    palette.setColor(app.palette().ButtonText, text_color)
    palette.setColor(app.palette().ToolTipText, text_color)
    palette.setColor(app.palette().Text, text_color)
    palette.setColor(app.palette().Base, widgetBackground_color)
    palette.setColor(app.palette().AlternateBase, placeHoldertext_color)
    palette.setColor(app.palette().HighlightedText, highlighttext_color)
    palette.setColor(app.palette().Link, labelLink_color)
    palette.setColor(app.palette().PlaceholderText, placeHoldertext_color)
    palette.setColor(QPalette.Disabled, QPalette.Text, placeHoldertext_color)

    app.setStyleSheet(
        f""" QPushButton,QComboBox,QSpinBox {{ 
                color: {getCol(textButton_color)}; 
                background-color: {getCol(button_color)};            
            }}
            QSpinBox{{
                width: 25px;
                padding: 5px;
            }}
            QLineEdit, QTextEdit {{ 
                border: 1px solid rgb(0 0 0 50%);
                background-color: {getCol(widgetBackground_color)};
            }}
            
            QLineEdit:Disabled, QTextEdit:Disabled {{ 
                color: {getCol(placeHoldertext_color)}; 
                background-color: {getCol(widgetBackground_color)};
            }}
            QLineEdit:Placeholder, QTextEdit:Placeholder {{ 
                color: {getCol(placeHoldertext_color)}; 
                background-color: {getCol(widgetBackground_color)};
            }}
            QCheckBox {{
                color:{getCol(textCheckbox_color)}; 
                /*background-color: {getCol(widgetBackground_color)};*/
            }}

            QCheckBox,QLineEdit,QPushButton,QComboBox,QSpinBox {{            
                border-radius: 2px;
                padding: 3px;
            }}

            QCheckBox::indicator {{
                background-color: white;
                border: 1px solid {getCol(checkboxBorder_color)};
                border-radius: 2px;
                width:10px;
                height:10px;
                
            }}
            QCheckBox::indicator:unchecked, QCheckBox::indicator:disabled {{
                background-color: {getCol(widgetBackground_color)};
                
            }} 
            QCheckBox::indicator:checked {{
                image: url(media/check_blue.png);
                background-color: {getCol(widgetBackground_color)};                      
            }}

            QGroupBox {{
                border: 2px solid {getCol(groupBorder_color)};
                border-radius: 5px;
                margin-top: 10px;            
            }}
            
            QGroupBox#LibraryGroup {{
                border: 1px solid {getCol(groupBorder_color)};
                border-radius: 5px;
                margin-top: 10px;  
            }}
            QGroupBox#LinkingGroup, QGroupBox#KeywordGroup {{
                border: 0px;
                border-radius: 5px;
                margin-top: 10px;            
            }}
            QGroupBox#LinkingGroup > QGroupBox, QGroupBox#KeywordGroup > QGroupBox {{
                border-width: 1px;            
                border-color: {getCol(subGroupBorder_color)};
            }}

            QFrame > *, QFrame > {{
                background-color:{getCol(frametitleBack_color)};
                border: 1px solid {getCol(frametitleBackBorder_color)};
                border-radius: 5px;                 
            }}        
            QGroupBox::title {{       
                color: {getCol(text_color)}; 
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;        
            }}
            #labelLink{{
                color: {getCol(textLink_color)};
                background-color:{getCol(widgetBackground_color)};
                text-decoration:none;
            }}
            #href{{
                color: {getCol(textLink_color)};
                background-color:{getCol(widgetBackground_color)};
                text-decoration:none;
            }}

            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
                background: {getCol(scrollbar_color)};
                border-radius: 5px;
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal  {{
                background: none;
                border: none;
                border-radius: 5px;
            }}
                        
            QScrollBar:vertical {{
                background: {getCol(scrollbarBackground_color)};
                width: 14px;                
                border-radius: 5px;
                border: 0px solid #999999;            
                margin: 0px 0px 0px 4px;             
            }}
            QScrollBar:horizontal {{
                background: {getCol(scrollbarBackground_color)};
                height: 14px;
                border-radius: 5px;
                border: 0px solid #999999;            
                margin: 4px 0px 0px 0px;  
            }}     
            QMessageBox{{
                background-color: {getCol(widgetBackground_color)};
            }}  
        
        """
        )

    app.setPalette(palette)