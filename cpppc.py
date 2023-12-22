from src import helper_funcs as hlp, action_funcs as act, data_class as d
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout

app = QApplication([])
# Preparing Window
window = QWidget()
layout = QVBoxLayout()

window.setLayout(layout)
window.show()
app.exec()