from src import helper_funcs as hlp, action_funcs as act
from PyQt5.QtWidgets import QApplication, QWidget, QFormLayout,QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit

from src.structs.GuiData import GuiData 
from src.structs.CMakeVersionData import CMakeVersionData
from src.structs.ProjectConfigurationData import ProjectConfigurationData
import src.cmake_helper as  cmake_helper

app = QApplication([])
app.setStyleSheet("QPushButton { color: magenta; }")

# Preparing Window
window = QWidget()
rootLayout = QHBoxLayout()
layout_projectName = QFormLayout()
layout_cmakeVersion = QHBoxLayout()

ProjConfDat = ProjectConfigurationData()

# Declare Project Name
group_projdef = QGroupBox(title="Project config")
ProjConfDat.projectName = hlp.addTextField("Project Name:", "myProject", layout_projectName)


# Declare Target dir
ProjConfDat.projectTargetDir = hlp.addTextField("Target directory:"      , ".", layout_projectName) #TODO: Check if directory is safe / suitable!
ProjConfDat.projectExecName  = hlp.addTextField("Executable Name:"       , "executable",layout_projectName)
ProjConfDat.projectDesc      = hlp.addTextBoxField("Project Description:",layout_projectName)

group_projdef.setLayout(layout_projectName)

group_cmake = QGroupBox(title="CMake version")
cmakeVersion_data = cmake_helper.getCMakeVersion()
cmake_version_major = hlp.addCmakeVersionBox("Major:", cmakeVersion_data.major, layout_cmakeVersion)
cmake_version_minor = hlp.addCmakeVersionBox("Minor:", cmakeVersion_data.minor, layout_cmakeVersion)
cmake_version_patch = hlp.addCmakeVersionBox("Patch:", cmakeVersion_data.patch, layout_cmakeVersion)
ProjConfDat.cmakeVersionData = cmakeVersion_data #TODO: Remember to update this when user change values...
group_cmake.setLayout(layout_cmakeVersion)



# Create button, run test function on press
butt = hlp.addButton("Test", layout_projectName)
# butt.clicked.connect(lambda: act.test(project_name) )
butt.clicked.connect(lambda: act.cmakebuttontest() )


createProjectButton = hlp.addButton("Create", layout_projectName)
createProjectButton.clicked.connect(lambda: act.createProject(ProjConfDat))

ProjConfDat.overwriteProjectTargetDir = hlp.addCheckBox("Overwrite", False, layout_projectName)
ProjConfDat.useProgram_ccache   = hlp.addCheckBox("Use CCache", True, layout_projectName)
ProjConfDat.useSanitizers       = hlp.addCheckBox("Use Sanitizers", True, layout_projectName)
# ProjConfDat.overwriteProjectTargetDir.widget.stateChanged.connect(lambda: ProjConfDat.toggle_overwriteProjectTargetDir())

rootLayout.addWidget(group_projdef)
rootLayout.addWidget(group_cmake)

window.setLayout(rootLayout)
window.show()
app.exec()