import os
from .ProjectConfigurationData import ProjectConfigurationData
from .CMakeData import CMakeData
from dataclasses import dataclass, field


@dataclass
class CppDataHelper():
    projData: ProjectConfigurationData
    cmakeDataHelper: CMakeData

    def __init__(self, projData: ProjectConfigurationData, cmakeDataHelper: CMakeData):
        self.projData = projData
        self.cmakeDataHelper = cmakeDataHelper
