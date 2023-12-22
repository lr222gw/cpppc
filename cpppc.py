from src import helper_funcs as hlp, action_funcs as act, data_class as d
from PyQt5.QtWidgets import QApplication, QWidget, QFormLayout,QVBoxLayout, QHBoxLayout

app = QApplication([])
app.setStyleSheet("QPushButton { color: magenta; }")

# Preparing Window
window = QWidget()
rootLayout = QHBoxLayout()
projectNameLayout = QFormLayout()
cmakeVersionLayout = QFormLayout()

# Declare Project Name
project_name = hlp.addTextField("Project Name:", projectNameLayout)

# Declare Target dir
target_dir = hlp.addTextField("Target directory:", projectNameLayout)

executable_name = hlp.addTextField("Executable Name:", projectNameLayout)

cmake_description = hlp.addTextField("Project Description:", projectNameLayout)

cmake_version_major = hlp.addTextField("CMake Major Version:", cmakeVersionLayout)
cmake_version_minor = hlp.addTextField("CMake Minor Version:", cmakeVersionLayout)
cmake_version_patch = hlp.addTextField("CMake Patch Version:", cmakeVersionLayout)


# Create button, run test function on press
butt = hlp.addButton("Run", projectNameLayout)
butt.clicked.connect(lambda: act.test(project_name) )

rootLayout.addLayout(projectNameLayout)
rootLayout.addLayout(cmakeVersionLayout)

window.setLayout(rootLayout)
window.show()
app.exec()