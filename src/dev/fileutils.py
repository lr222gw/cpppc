
import filecmp
import os
from pathlib import Path
import shutil
import hashlib
from typing import Optional

from src.dev.Terminate import terminate


def copyDirTree(src:Path, dest:Path, ignoredSubdirs:Optional[list[str]] = None):
    
    if not src.is_dir(): 
        terminate(f"Not a valid directory: [{str(src)}]")
    
    comparedDirs = filecmp.dircmp(str(src.absolute()),str(dest.absolute()), ignore=ignoredSubdirs)
    if dest.is_dir() and len(comparedDirs.diff_files) == 0:
        print(f"Skip copy; same content : [{src.absolute()} => {dest.absolute()}]")
        return
    
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

def hash_directory(directory): # Written by Chatgpt...        
    file_hashes = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                sha256_hash = hashlib.sha256()
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)

                file_hashes.append(sha256_hash.hexdigest())

    # Concatenate individual file hashes and hash the result
    directory_hash = hashlib.sha256("".join(file_hashes).encode()).hexdigest()
    return directory_hash


def listDirectory(directory:str):
    filesList = list[str]()
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            filesList.append(file_path)
    return filesList 

def removeUnmatchingFilesInDir(orignalDirFiles:list[str], modifiedDirFiles:list[str]):
    for modifiedDirFile in modifiedDirFiles:
        if modifiedDirFile not in orignalDirFiles:
            os.remove(modifiedDirFile)    