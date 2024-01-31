import json
from os import path
from pathlib import Path
from typing import Optional
from src.dev.Terminate import terminate
from src.structs.ProjectConfigurationDat import *


DIR_HISTORY_CPPPC :str
FILE_HISTORY_CPPPC_DEPENDENT_DATA = "cpppc_data.json"


class PersistantDataManager():
    """ 
    PersistantDataManager is a glboal singleton. 
    It keeps track of all projects and the status of their dependencies
    """
    __instance = None
    projectDatasDict : dict[str,ProjectConfigurationData]
    dependenciesDirs : dict[str,DepDat] # Path, status? 
    userLocalLibPath : str

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            #TODO: Load projectDatasDict from file ()
            cls.__instance.projectDatasDict =  dict[str,ProjectConfigurationData]()
            cls.__instance.dependenciesDirs =  dict[str,DepDat]()
            cls.__instance._load_config_from_file()
        return cls.__instance
    
    def addData(self, projDat: ProjectConfigurationData):
        projKey = projDat.projectName+"_"+path.abspath(projDat.getTargetPath())
        self.projectDatasDict[projKey] = projDat
    
    def addDependencyData(self, dep: DepDat):
        depKey = path.abspath(dep.path)
        self.dependenciesDirs[depKey] = dep

    def checkDependencyExist(self, absDepPath:str)->bool:
        if absDepPath in self.dependenciesDirs.keys():
            return True
        return False
    
    def getuserLocalLibPath(self):
        return self.userLocalLibPath
    
    def getDependencyData(self, absDepPath:str) -> DepDat:
        if absDepPath in self.dependenciesDirs.keys():
            return self.dependenciesDirs[absDepPath]
        else:
            print(f"Missing History entry for dependency with path {absDepPath}")
            exit("failed")
    
    def _load_config_from_file(self):
        try:
            global DIR_HISTORY_CPPPC
            with open(path.join(DIR_HISTORY_CPPPC,FILE_HISTORY_CPPPC_DEPENDENT_DATA), 'r') as file:
                data = json.load(file)
                self.projectDatasDict = data.get('projectDatasDict', {})
                tempDependenciesDirs = data.get('dependenciesDirs', {})
                for entry in tempDependenciesDirs:
                    d = DepDat(                        
                        path=tempDependenciesDirs[entry]["path"],
                        targets=tempDependenciesDirs[entry]["targets"],
                        targetDatas=TargetDatas(
                            tempDependenciesDirs[entry]["targetDatas"]["possibleTargets"],
                            tempDependenciesDirs[entry]["targetDatas"]["SHARED"],
                            tempDependenciesDirs[entry]["targetDatas"]["STATIC"],
                            tempDependenciesDirs[entry]["targetDatas"]["INTERFACE"],
                            tempDependenciesDirs[entry]["targetDatas"]["keyWords"]
                            
                        )
                    )
                    self.dependenciesDirs[entry] = d
                

                self.dependenciesDirs
                self.userLocalLibPath = data.get('userLocalLibPath', ".")
        except FileNotFoundError:
            # File not found, initialize with empty dictionaries
            self.projectDatasDict = {}
            self.dependenciesDirs = {}
            self.userLocalLibPath = "."

    def save_config_to_file(self):
        global DIR_HISTORY_CPPPC
        data = {
            'projectDatasDict': self.projectDatasDict,
            'dependenciesDirs': self.dependenciesDirs,
            'userLocalLibPath': self.userLocalLibPath,
        }
        def dataSerializer(obj):
            print(obj.__str__())
            if isinstance(obj,ProjectConfigurationData):
                return obj.__dict__
            elif isinstance(obj, DepDat): 
                return obj.__dict__
            else:
                return obj.__dict__

        with open(path.join(DIR_HISTORY_CPPPC,FILE_HISTORY_CPPPC_DEPENDENT_DATA), 'w') as file:
            json.dump(data, file, default=dataSerializer, indent=4)


def prepareStorage():
    from pathlib import Path
    import sys
    data_dir = getCpppcDir()
    data_dir.mkdir(parents=True, exist_ok=True)
    global DIR_HISTORY_CPPPC 
    DIR_HISTORY_CPPPC = data_dir.absolute().__str__()
    temp = data_dir / "temp"
    if temp.exists():
        shutil.rmtree(temp.absolute().__str__())

def getCpppcDir()->Path:
    from pathlib import Path
    import sys
    home_dir = Path.home()
    app_name = 'cpppc'
    app_author = 'cpppc_project'

    if sys.platform.startswith('win'):
        # Windows
        data_dir = home_dir / 'AppData' / 'Roaming' / app_author / app_name
    elif sys.platform.startswith('darwin'):
        # macOS
        data_dir = home_dir / 'Library' / 'Application Support' / app_author / app_name
    else:
        # Linux and other Unix-like systems
        data_dir = home_dir / '.local' / 'share' / app_author / app_name

    return data_dir