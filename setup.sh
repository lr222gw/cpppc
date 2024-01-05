#!/bin/bash

install_path_pipx_venvs="$HOME/.local/pipx/venvs"
venv_name="pyqt5"
install_path="${install_path_pipx_venvs}/${venv_name}" #default path for virtual


printf "Install python requirements into virtual venv\n"
printf "Install to default path : $install_path ? (Y/N)\n"
read will_install_to_path

if [[ "$will_install_to_path" == "n" ]] then
    printf "Provide path:"
    read install_path 
    safe_install_location=1;
    if [[ "${install_path:0:1}" == "/"  ]] then 
        safe_install_location=0;
        if [[ "${install_path:0:6}" == "/home/"  ]] then 
            safe_install_location=1;
        fi; 
    fi; 
    if [[ ${safe_install_location} == 0  ]] then 
        printf "Abort, script does not want to write files outside homedir...\n"
        exit
    fi; 
    if [[ -d "$install_path" ]] then 
        printf "Abort, directory already exists...\n"
        exit
    fi;
elif [[ "$will_install_to_path" == "y" ]] then 
    if [[ ! -d "$install_path_pipx_venvs" ]] then 
        printf "Abort, directory $install_path_pipx_venvs does not exists...\n"
        exit
    fi;
else 
    printf "Invalid answer. Exiting\n"
    exit
fi; 

printf "Preparing virtual environment in : $install_path \n"
python3 -m venv ${install_path}

${install_path}/bin/python3 -m pip install pyqt5

