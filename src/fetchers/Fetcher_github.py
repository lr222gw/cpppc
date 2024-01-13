import glob
import io
import os
import shutil
from zipfile import ZipFile
import zipfile
import requests
import re

from src.dev.Terminate import terminate
def fetchGithubRepo(url:str, libname:str,targetPath:str = "."):
    
    github_repo_regx = re.compile(r"^(https{0,1}://){0,1}github\.com/([a-zA-Z_0-9-.]+)/((?!\.git)[a-zA-Z_0-9-.]+)(/(tree|commit)/([a-zA-Z0-9]+)){0,1}")

    myMatch = re.match(github_repo_regx, url)
    if myMatch != None: 
        owner = myMatch.group(2)
        repo =  myMatch.group(3)
        ref  =  myMatch.group(6)

        git_ending_regx = re.compile(r"(.*)\.git$")
        repoMatch = re.match(git_ending_regx,repo)
        if repoMatch != None:
            repo = repoMatch[1]
        
        repo_infoUrl = f'https://api.github.com/repos/{owner}/{repo}'
        repo_info = requests.get(repo_infoUrl)   
        if repo_info.status_code != 200:
            print(f"Url '"+url+"' does not lead to a valid repository.")
            return

        if ref == None:
            ref = repo_info.json()["default_branch"]
        
        contents_url = f'https://api.github.com/repos/{owner}/{repo}/zipball/{ref}'

        print(f"Downloading '{repo}' from '{url}'")
        contents_response = requests.get(contents_url)

        if contents_response.status_code == 200:            
            print(f"Unzipping '{repo}' contents to {targetPath}'")
            z = zipfile.ZipFile(io.BytesIO(contents_response.content), "r")            
            _extractToDirectory(libname,targetPath,z)
        else:
            print(f"Failed to fetch contents. Status code: {contents_response.status_code}")
    else:
        print(f"Url '{url}' does not lead to a valid repository")

def _extractToDirectory(libname :str,targetPath :str, zipFile : ZipFile):
    finalpath = targetPath+"/"+libname+"/"
    tempdir="temp"
    tempdirFiles = tempdir+"/"

    with zipFile as zip_ref:
        # Get the names of all files and directories in the ZIP archive        
        tempdirFiles += _getZipRootDirName(zip_ref)+"/*"

        zip_contents = zip_ref.namelist() 
        for item in zip_contents:        
            zip_ref.extract(item, tempdir)

    libraryFiles=glob.glob(tempdirFiles, include_hidden=True)
    if not os.path.exists(finalpath):
        os.mkdir(finalpath)
    else:
        shutil.rmtree(finalpath)
        os.mkdir(finalpath)
        
    for file in libraryFiles:
        shutil.move(file, targetPath+"/"+libname+"/")

    shutil.rmtree(tempdir)
    
def _getZipRootDirName(zip_ref):        
    mainroot = ""
    countRootDirs = 0
    for name in zip_ref.namelist():
        if name[name.find("/")+1:] == "":
            mainroot = name[:name.find("/")]
            countRootDirs += 1
        
    if countRootDirs > 1:
        terminate("Not design to handle multiple root dirs in a zip file...")

    return mainroot

