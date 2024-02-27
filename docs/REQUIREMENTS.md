# CPPPC - C++ Projection Configurator - Prerequisites

# ⚠️ <span style="color:red;">WORK IN PROGRESS</span>⚠️

Before using CPPPC, ensure that the following dependencies are installed on your Linux system:

## Install Python dependencies 
Run the following command to install required dependencies
```bash
pip install -r requirements.txt
```


## 1. Install CMake

CMake is required for building C++ projects. You can install it using the package manager for your distribution:

#### Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install cmake
```

#### Red Hat/Fedora:

```bash
sudo dnf install cmake
```

#### Arch Linux:

```bash
sudo pacman -S cmake
```

Verify the installation by checking the CMake version:

```bash
cmake --version
```

## 2. Install Python

**CPPPC** relies on Python for its functionality. Most Linux distributions come with Python pre-installed. If not, you can install it using your package manager. For example, on Debian/Ubuntu-based systems:

```bash
sudo apt-get update
sudo apt-get install python3
```

Verify the installation by checking the Python version:

```bash
python3 --version
```

## 3. Install PyQt5 for Python

You have three choices, Alternative A: use Script, Alternative B: manual install through pipx, Alternative C: Manual install. 

### Alternative A: Install through script
Run the `setup.sh` script located in the root dir. (Given that you've cloned the repo)
```bash
    ./setup.sh 
    # Follow guide until done... 
```

### Alternative B: Manual install through Pipx
To manually install PyQt5 in a virtual environment through pipx, follow these steps:

- Install pipx:

```bash
python3 -m pip install --user pipx
python3 -m userpath append ~/.local/pipx/venvs
```

- Install PyQt5 using pipx:

```bash
pipx install PyQt5
```

Verify the PyQt5 installation:

```bash
python -c "import PyQt5.QtWidgets; print(PyQt5.QtWidgets.QApplication([]).exec_())"
```

If no errors are displayed, PyQt5 is successfully installed.

### Alternative C: Manual install
To manually install PyQt5 in a virtual environment, follow these steps:

- Create virtual environemnt in a location in userspace, ex `~/.local/venvs` :

```bash
python3 -m venv ~/.local/venvs
```

- Add the newly created virtual environment to the userpath:

```bash
python3 -m userpath append ~/.local/pipx/venvs
```

- Install PyQt5 python in that virtual environment:

```bash
~/.local/venv/bin/python3 -m pip install pyqt5
```

Verify the PyQt5 installation:

```bash
~/.local/venv/bin/python3 -c "import PyQt5.QtWidgets; print(PyQt5.QtWidgets.QApplication([]).exec_())"
```

If no errors are displayed, PyQt5 is successfully installed.
