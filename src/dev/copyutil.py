
from pathlib import Path
import shutil
from typing import Optional

from src.dev.Terminate import terminate


def copyDirTree(src:Path, dest:Path, ignoredSubdirs:Optional[list[str]] = None):
        
    if not src.is_dir(): 
        terminate(f"Not a valid directory: [{str(src)}]")
    
    def ignore_dirs_wrapper(ignoredSubdirs:Optional[list[str]] = None):
        def ignore_dirs(dir, names):        
            if ignoredSubdirs != None : 
                excluded_dirs = ignoredSubdirs
                return set(excluded_dirs)
            else:            
                return set()
        return ignore_dirs
    
    shutil.copytree(
        str(src.absolute()),
        str(dest.absolute()),
        dirs_exist_ok=True, 
        ignore=ignore_dirs_wrapper(ignoredSubdirs = ignoredSubdirs)
    )