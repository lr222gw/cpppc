from src import helper_funcs as hlp, action_funcs as act
from PyQt5.QtWidgets import QApplication, QWidget, QFormLayout,QVBoxLayout, QHBoxLayout, QGroupBox, QFrame, QStackedLayout, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *

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
layout_targetProperties = QFormLayout()
layout_cmakeBridge = QVBoxLayout()
layout_cmakeBridge.setAlignment(Qt.AlignmentFlag.AlignTop)


layout_rightside = QFormLayout()

ProjConfDat = ProjectConfigurationData()

# Declare Project Name
group_projdef = QGroupBox(title="Project config")
ProjConfDat.projectName = hlp.addTextField("Project Name:", "myProject", layout_projectName)


# Declare Target dir
ProjConfDat.projectTargetDir = hlp.addTextField("Target directory:"      , ".", layout_projectName) #TODO: Check if directory is safe / suitable!
ProjConfDat.projectExecName  = hlp.addTextField("Executable Name:"       , "executable",layout_projectName)
ProjConfDat.projectDesc      = hlp.addTextBoxField("Project Description:",layout_projectName)

ProjConfDat.entryPointFile  = hlp.addTextField("Entry Point file:"       , "main.cpp",layout_projectName)

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

# TODO: Replace with addProp_* functions
ProjConfDat.overwriteProjectTargetDir = hlp.addCheckBox("Overwrite", False, layout_projectName)
ProjConfDat.useProgram_ccache     = hlp.addCheckBox("Use CCache", True, layout_projectName)
ProjConfDat.useSanitizers         = hlp.addCheckBox("Use Sanitizers", True, layout_projectName)
ProjConfDat.useMeasureCompiletime = hlp.addCheckBox("Measure Compiletime", True, layout_projectName) #TODO: Move into group_properties

group_properties = QGroupBox(title="Target Properties")

# TODO: Fetch Default values from .cfg files (or similar format)
ProjConfDat.addProp_combobox_list("C++ Standard", 
                            "CXX_STANDARD",                     [98,11,14,17,20,23,26] , 4, layout_targetProperties)
ProjConfDat.addProp_checkbox("Use C++ Extensions",               
                            "CXX_EXTENSIONS",                    False, layout_targetProperties)
ProjConfDat.addProp_checkbox("Generate Compile Commands",        
                            "EXPORT_COMPILE_COMMANDS",           True, layout_targetProperties)
ProjConfDat.addProp_checkbox("Use Link What You Use",            
                            "LINK_WHAT_YOU_USE",                 True, layout_targetProperties)
ProjConfDat.addProp_checkbox("Use Include What You Use",         
                            "CMAKE_CXX_INCLUDE_WHAT_YOU_USE",    True, layout_targetProperties)
ProjConfDat.addProp_checkbox("Use Interprocedural Optimization", 
                            "INTERPROCEDURAL_OPTIMIZATION",      True, layout_targetProperties)

group_properties.setLayout(layout_targetProperties)

layout_rightside.addWidget(group_cmake)
layout_rightside.addWidget(group_properties)

group_cmakeBridge = QGroupBox(title="CMake vars to C++")
ProjConfDat.useCmakeCppBridge = hlp.addCheckBox("Create \"CMake bridge\" to C++", False, layout_cmakeBridge)


layout_cmakeBridge_content = QVBoxLayout()
frame_cmakeBridge_content = QFrame()
hlp.showHideFrame(frame_cmakeBridge_content, ProjConfDat.useCmakeCppBridge.getState())

ProjConfDat.addCmakeCppVarHeader(layout_cmakeBridge_content)

frame_cmakeBridge_content.setLayout(layout_cmakeBridge_content)

ProjConfDat.useCmakeCppBridge.registerConnection(
    lambda: hlp.showHideFrame(frame_cmakeBridge_content, ProjConfDat.useCmakeCppBridge.getState())
)

group_cmakeBridge.setLayout(layout_cmakeBridge)
layout_cmakeBridge.addWidget(frame_cmakeBridge_content)

#TODO: GUI to select libs from system and files
# ProjConfDat.publicLinkLibs = ["lib1", "lib2", "lib3"]
# ProjConfDat.privateLinkLibs  = ["lib4", "lib5", "lib6"]


rootLayout.addWidget(group_projdef)
rootLayout.addLayout(layout_rightside)
rootLayout.addWidget(group_cmakeBridge)

window.setLayout(rootLayout)
window.show()
app.exec()