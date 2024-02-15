import json
import os
from typing import Any, Optional

from src.dev.Terminate import terminate

class TargetDatas():
    possibleTargets: list[str]
    SHARED: list[str]
    STATIC: list[str]
    INTERFACE: list[str]
    keyWords : Optional[dict[str,str]]
    includes : Optional[list[str]]
    parsedComponentTargets: list[str] = list[str]()
    find_package : Optional[str] = None    
    def __init__(self, 
                 possibleTargets: list[str] = [], 
                 SHARED: list[str] = [], 
                 STATIC: list[str] = [], 
                 INTERFACE: list[str] = [], 
                 parsedComponentTargets: list[str] = [], 
                 keyWords : Optional[dict[str,str]] = None, 
                 includes : Optional[list[str]] = None,
                 find_package : Optional[str] = None): 
        self.possibleTargets  = possibleTargets
        self.SHARED           = SHARED
        self.STATIC           = STATIC
        self.INTERFACE        = INTERFACE
        self.keyWords         = keyWords
        self.includes         = includes
        self.parsedComponentTargets         = parsedComponentTargets
        self.find_package    = find_package
        
class DepDat():
    path : str
    targets : list[str]
    targetDatas: TargetDatas
    def __init__(self,path : str, targets : list[str], targetDatas: TargetDatas):
        self.path    = path
        self.targets = targets
        self.targetDatas = targetDatas

class ProjectConfigurationData():    
    _projectName:Optional[ str ]                           = None
    _projectTargetDir:Optional[ str ]                      = None
    _projectExecName :Optional[ str ]                      = None
    _projectDesc:Optional[ str ]                           = None
    _entryPointFile:Optional[ str ]                        = None
    _overwriteProjectTargetDir:Optional[ bool ]            = None
    _useProgram_ccache :Optional[ bool ]                   = None
    _useMeasureCompiletime :Optional[ bool ]               = None
    _cmakeVersionData:Optional[  tuple[int,int,int]]       = None
    _cmakeToCppVars :Optional[ dict[str,tuple[str,str]] ]  = None
    _linkLibs : Optional[dict[str,tuple[str,bool, list[str],TargetDatas]]] = None
    _linkLibs_public   :Optional[ dict[str,list[str]]]              = None
    _linkLibs_private  :Optional[ dict[str,list[str]]]              = None
    _linkIncl_public   :Optional[ dict[str,list[str]]]              = None
    _linkIncl_private  :Optional[ dict[str,list[str]]]              = None
    _props :Optional[ dict[str,str|bool|int]]                       = None

    _linkLibs_public_override   :dict[str,list[str]]
    _linkLibs_private_override  :dict[str,list[str]]
    _linkIncl_public_override   :dict[str,list[str]]
    _linkIncl_private_override  :dict[str,list[str]]
    _linkLibs_components        :dict[str,list[str]]
    _linkLibs_findPackage       :dict[str,str]

    def __init__(self, 
                projectName:Optional[ str ]                           = None,
                projectTargetDir:Optional[ str ]                      = None,
                projectExecName :Optional[ str ]                      = None,
                projectDesc:Optional[ str ]                           = None,
                entryPointFile:Optional[ str ]                        = None,
                overwriteProjectTargetDir:Optional[ bool ]            = None,
                useProgram_ccache :Optional[ bool ]                   = None,
                useMeasureCompiletime :Optional[ bool ]               = None,
                cmakeVersionData:Optional[  tuple[int,int,int]]       = None,
                cmakeToCppVars :Optional[ dict[str,tuple[str,str]] ]  = None,
                linkLibs: Optional[dict[str,tuple[str,bool, list[str],TargetDatas]]]  = None, 
                linkLibs_public  :Optional[dict[str,list[str]]]       = None,
                linkLibs_private  :Optional[dict[str,list[str]]]      = None,
                # linkIncl_public  :Optional[dict[str,list[str]]]       = None,
                # linkIncl_private  :Optional[dict[str,list[str]]]      = None,
                props :Optional[ dict[str,str|bool|int]]              = None
                 ):
        self.projectName               =projectName
        self.projectTargetDir          =projectTargetDir
        self.projectExecName           =projectExecName
        self.projectDesc               =projectDesc
        self.entryPointFile            =entryPointFile
        self.overwriteProjectTargetDir =overwriteProjectTargetDir
        self.useProgram_ccache         =useProgram_ccache
        self.useMeasureCompiletime     =useMeasureCompiletime
        self.cmakeVersionData          =cmakeVersionData
        self.cmakeToCppVars            =cmakeToCppVars
        self.linkLibs                  =linkLibs
        self.linkLibs_public           =linkLibs_public
        self.linkLibs_private          =linkLibs_private
        self.linkIncl_public           =dict[str,list[str]]()
        self.linkIncl_private          =dict[str,list[str]]()
        self.props                     =props
        self._linkLibs_public_override  = dict[str,list[str]]()
        self._linkLibs_private_override = dict[str,list[str]]() 
        self._linkIncl_public_override  = dict[str,list[str]]()
        self._linkIncl_private_override = dict[str,list[str]]() 

        self._linkLibs_components       = dict[str,list[str]]() 
        self._linkLibs_findPackage       = dict[str,str]() 
    
    def update(self, updatedInstance):

        self.projectName               =updatedInstance.projectName
        self.projectTargetDir          =updatedInstance.projectTargetDir
        self.projectExecName           =updatedInstance.projectExecName
        self.projectDesc               =updatedInstance.projectDesc
        self.entryPointFile            =updatedInstance.entryPointFile
        self.overwriteProjectTargetDir =updatedInstance.overwriteProjectTargetDir
        self.useProgram_ccache         =updatedInstance.useProgram_ccache
        self.useMeasureCompiletime     =updatedInstance.useMeasureCompiletime
        self.cmakeVersionData          =updatedInstance.cmakeVersionData
        self.cmakeToCppVars            =updatedInstance.cmakeToCppVars
        self.linkLibs                  =updatedInstance.linkLibs
        self.linkLibs_public           =updatedInstance.linkLibs_public
        self.linkLibs_private          =updatedInstance.linkLibs_private
        self.linkIncl_public           =updatedInstance.linkIncl_public
        self.linkIncl_private          =updatedInstance.linkIncl_private
        self.props                     =updatedInstance.props


        for libkey, userSelectedTargets in self._linkLibs_public_override.items(): 
            self.linkLibs_public[libkey] = userSelectedTargets
        for libkey, userSelectedTargets in self._linkLibs_private_override.items(): 
            self.linkLibs_private[libkey] = userSelectedTargets

        for libkey, userSelectedTargets in self._linkIncl_public_override.items(): 
            self.linkIncl_public[libkey] = userSelectedTargets
        for libkey, userSelectedTargets in self._linkIncl_private_override.items(): 
            self.linkIncl_private[libkey] = userSelectedTargets

    def getLibComponents(self, localLibName:str) -> list[str]:
        if localLibName in self._linkLibs_components:
            return self._linkLibs_components[localLibName]
        return []
            
    @property
    def projectName(self)->str :
        return self.__getVar(self._projectName)
    @projectName.setter
    def projectName(self, v):
        self._projectName =v 
    @property
    def projectTargetDir(self)->str :
        return self.__getVar(self._projectTargetDir)
    @projectTargetDir.setter
    def projectTargetDir(self, v):
        self._projectTargetDir =v 
    @property
    def projectExecName(self)->str :
        return self.__getVar(self._projectExecName)
    @projectExecName.setter
    def projectExecName(self, v):
        self._projectExecName =v 
    @property
    def projectDesc(self)->str :
        return self.__getVar(self._projectDesc)
    @projectDesc.setter
    def projectDesc(self, v):
        self._projectDesc =v 
    @property
    def entryPointFile(self)->str :
        return self.__getVar(self._entryPointFile)
    @entryPointFile.setter
    def entryPointFile(self, v):
        self._entryPointFile =v 
    @property
    def overwriteProjectTargetDir(self)->bool :
        return self.__getVar(self._overwriteProjectTargetDir)
    @overwriteProjectTargetDir.setter
    def overwriteProjectTargetDir(self, v):
        self._overwriteProjectTargetDir =v 
    @property
    def useProgram_ccache(self)->bool :
        return self.__getVar(self._useProgram_ccache)
    @useProgram_ccache.setter
    def useProgram_ccache(self, v):
        self._useProgram_ccache =v 
    @property
    def useMeasureCompiletime(self)->bool :
        return self.__getVar(self._useMeasureCompiletime)
    @useMeasureCompiletime.setter
    def useMeasureCompiletime(self, v):
        self._useMeasureCompiletime =v 
    @property
    def cmakeVersionData(self)->tuple[int,int,int]:
        return self.__getVar(self._cmakeVersionData)
    @cmakeVersionData.setter
    def cmakeVersionData(self, v):
        self._cmakeVersionData =v 
    @property
    def cmakeToCppVars(self)->dict[str,tuple[str,str]] :
        return self.__getVar(self._cmakeToCppVars)
    @cmakeToCppVars.setter
    def cmakeToCppVars(self, v):
        self._cmakeToCppVars =v 
    @property
    def linkLibs(self)->Optional[dict[str,tuple[str,bool, list[str],TargetDatas]]]:
        """
        dict[userSlectedName: str, tuple[librarypath: str, isPublicLib: bool, list[libraryTargetNames: str]]]
        """
        return self.__getVar(self._linkLibs)
    @linkLibs.setter
    def linkLibs(self, v):
        self._linkLibs =v 

    @property
    def linkLibs_public(self)->dict[str,list[str]]:
        return self.__getVar(self._linkLibs_public)
    @linkLibs_public.setter
    def linkLibs_public(self, v):
        self._linkLibs_public =v 
    @property
    def linkLibs_private(self)->dict[str,list[str]]:
        return self.__getVar(self._linkLibs_private)
    @linkLibs_private.setter
    def linkLibs_private(self, v):
        self._linkLibs_private =v 

    @property
    def linkIncl_public(self)->dict[str,list[str]]:
        return self.__getVar(self._linkIncl_public)
    @linkIncl_public.setter
    def linkIncl_public(self, v):
        self._linkIncl_public =v 
    @property
    def linkIncl_private(self)->dict[str,list[str]]:
        return self.__getVar(self._linkIncl_private)
    @linkIncl_private.setter
    def linkIncl_private(self, v):
        self._linkIncl_private =v 
    @property
    def props(self)->dict[str,str]:
        return self.__getVar(self._props)
    @props.setter
    def props(self, v):
        self._props =v 

    def __getVar(self, var:Any)->Any:
        if  var == None:
            terminate("ProjectConfigurationData was empty!")
        return var

    def getTargetPath(self) -> str:
        return os.path.join(self.projectTargetDir, self.projectName)
        
