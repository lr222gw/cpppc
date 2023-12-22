from src import helper_funcs as hlp, action_funcs as act, data_class as d
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout

app = QApplication([])
app.setStyleSheet("QPushButton { color: magenta; }")

# Preparing Window
window = QWidget()
layout = QVBoxLayout()

# Declare Project Name
project_name = hlp.addTextField("Project Name:", layout)

# Create button, run test function on press
butt = hlp.addButton("Run", layout)
butt.clicked.connect(lambda: act.test(project_name) )

window.setLayout(layout)
window.show()
app.exec()