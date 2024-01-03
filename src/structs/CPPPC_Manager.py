from dataclasses import dataclass, field
from .CMakeData import *
from .CppDataHelper import *
from .ProjectConfigurationData import *
import os

@dataclass
class CPPPC_Manager:
    cmakeListDat    : CMakeData
    cmake_inputsDat : CMakeData
    cppDat          : CppDataHelper
    projDat         : ProjectConfigurationData
    
    
    def __init__(self, projdat : ProjectConfigurationData):
        self.projDat = projdat        
        self.cmakeListDat       = CMakeData(self.projDat)
        self.cmake_inputsDat    = CMakeData(self.projDat)
        self.cppDat             = CppDataHelper(self.projDat, self.cmakeListDat)
