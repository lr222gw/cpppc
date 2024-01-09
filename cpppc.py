from src import helper_funcs as hlp, action_funcs as act
from PyQt5.QtWidgets import QApplication, QWidget, QFormLayout,QVBoxLayout, QHBoxLayout, QGroupBox, QFrame, QStackedLayout, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *

from src.structs.GuiData import *
from src.structs.CMakeVersionData import CMakeVersionData
from src.structs.ProjectConfigurationData import ProjectConfigurationData
import src.cmake_helper as  cmake_helper
from src.structs.CPPPC_Manager import CPPPC_Manager

app = QApplication([])
app.setStyleSheet("QPushButton { color: magenta; }")

# Preparing Window
window = QWidget()
rootLayout = QHBoxLayout()
layout_projectName = QFormLayout()
layout_cmakeVersion = QHBoxLayout()
layout_targetProperties = QFormLayout()

layout_2nd_column = QVBoxLayout()
layout_3rd_column = QVBoxLayout()

ProjConfDat = ProjectConfigurationData()
cppc = CPPPC_Manager(ProjConfDat)

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
layout_cmakeVersion.setStretch(0,1)
layout_cmakeVersion.setStretch(1,1)
group_cmake.setMaximumHeight(100)



createProjectButton = hlp.addButton("Create", layout_projectName)
createProjectButton.clicked.connect(lambda: cppc.createProject())

# TODO: Replace with addProp_* functions
ProjConfDat.overwriteProjectTargetDir = hlp.addCheckBox("Overwrite", False, layout_projectName)
ProjConfDat.useProgram_ccache     = hlp.addCheckBox("Use CCache", True, layout_projectName)
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

ProjConfDat.addExtraFeatureGroup_UserInputs(
    layout_3rd_column,
    layout_projectName,
    "CMake vars to C++",
    "Use CMake to C++ Communcation",
    False,
    ProjConfDat.addCmakeToCppVar,
    UserInput("Variable Name"),
    UserInput("Value"),
    requirement= (lambda:  cppc.requireCMakeCppBridge())
)

if False : #Old version, still valid if a checkbox is not connected to more than one function

    ProjConfDat.addExtraFeatureGroup_checkbox(
    layout_2nd_column,       
    layout_projectName,
    "Sanitizer settings",   
    "Use Sanitizers",
    True,
    cppc.cmakeListDat.genStr_linkSanitizers,
    ToggleData("Debug", "g", True),
    ToggleData("Sanitize Adress,Leak and Undef", "fsanitize=address,leak,undefined", True),
    ToggleData("No omit frame ptr", "fno-omit-frame-pointer", True),
    ToggleData("memory track origins=2", "fsanitize-memory-track-origins=2", True),
    ToggleData("Use Blacklist", "fsanitize-blacklist=${CMAKE_CURRENT_SOURCE_DIR}/sanitizer_blacklist.txt", False,
        requirement=lambda: cppc.createFileOnDemand("sanitizer_blacklist.txt", "test")),
    )

g = cppc.cmakeListDat #Shorthand

ProjConfDat.addExtraFeatureShareGroup_checkbox(
    layout_3rd_column,       
    layout_projectName,
    "Sanitizer settings",   
    "Use Sanitizers",
    False,
    ToggleShareData("Debug", "g", True, 
        g.genStr_linkSanitizers, g.genStr_compileSanitizers),
    ToggleShareData("Sanitize Adress,Leak and Undef", "fsanitize=address,leak,undefined", True,
        g.genStr_linkSanitizers, g.genStr_compileSanitizers),
    ToggleShareData("No omit frame ptr", "fno-omit-frame-pointer", True,
        g.genStr_linkSanitizers, g.genStr_compileSanitizers),
    ToggleShareData("Memory track origins=2", "fsanitize-memory-track-origins=2", True,
        g.genStr_linkSanitizers),
    ToggleShareData("Recover adress", "fsanitize-recover=address", True,
        g.genStr_compileSanitizers),
    ToggleShareData("Use Blacklist", "fsanitize-blacklist=${CMAKE_CURRENT_SOURCE_DIR}/sanitizer_blacklist.txt", False,
        g.genStr_linkSanitizers, g.genStr_compileSanitizers, 
        requirement=lambda: cppc.createFileOnDemand("sanitizer_blacklist.txt", "test")
        ),
    )    


layout_2nd_column.addWidget(group_cmake)
layout_2nd_column.addWidget(group_properties)

#TODO: GUI to select libs from system and files
# ProjConfDat.publicLinkLibs = ["lib1", "lib2", "lib3"]
# ProjConfDat.privateLinkLibs  = ["lib4", "lib5", "lib6"]

ProjConfDat.addExtraFeatureGroup_UserInputs(
    layout_3rd_column,
    layout_projectName,
    "Libraries",
    "Use external Libraries",
    True,
    ProjConfDat.addLibraryComponent,
    UserInput_checkbox("Public",False,rotation=-90),
    UserInput("Libary Name"),
    UserInput("Path to library"),    
)

rootLayout.addWidget(group_projdef)
rootLayout.addLayout(layout_2nd_column)
rootLayout.addLayout(layout_3rd_column)

window.setLayout(rootLayout)
window.show()
app.exec()