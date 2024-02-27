# CPPPC - C++ Project Configurator
[comment]: <> (Simple GUI application written in Python aimed at setting up CMake based C++ Projects.)
CPPPC is a GUI tool designed to generate boilerplate projects for C++. It utilizes Python to generate a CMakeLists.txt file along with a directory structure. The primary goal of CPPPC is to be flexible in generating various types of C++ projects (Libraries, Executables) while remaining easy to extend.

![Example Image](docs/media/gui_demo.png)

## Project Status
*CPPPC is under active development, it is currently in a very early state.*

CPPPC Latest release is v.0.2.0 - Library import update. 

As of release v.0.2.0 it has the following features: 
- Creates directories and files for a CMake project based on user provided configuration through GUI:
    - Specify CMake version
    - Set CMake project name, description, executable name
    - Set target directory
    - Set *Some* Target properties;<br>
      *C++ version, generation of Compile Commands, link what you use, include what you use and interprocedural optimization*
    - Set *Some* Sanitizer options;<br>
      *Debug, SanitizeAddress,leak and Undefined, no omit frame ptr, memory track origins=2, recover adress, blacklist*
    - Expose CMake variables to your C++ application
    - Adding libraries to your project
- Fetching libraries from GitHub to be imported as libraries. *(If library uses CMake...)*
- Parse CMake Libraries to collect Target names and components
- Persistent cache for configuration data *(Per project, based on provided name, lib path and md5 hash of library source contents)*

## Demonstration 
![Shows the add library feature; downloads a library and configures it.](docs/media/library_import_showcase.gif)

The gif above demonstrates the process of setting up a project that requires the SFML library through the graphical user interface (GUI).

## Upcoming Features

CPPPC currently under development, upcoming features include:

- Fetching libraries from other services than GitHub to be imported as libraries.
- Generating IDE-specific files, such as workspace files for Visual Studio Code.
- Generate Cross-platform Library projects.
- Turn non-cmake libraries into basic CMake projects to easier be included in your project.
- MacOs support (Currently only tested on Linux and Windows).
- and more...

## Precompiled binaries 
The easiest way to run the application is with the precompiled binaries from the [Releases page](https://github.com/lr222gw/cpppc/releases).


Note that you still need to have CMake and your compiler installed.
*(If you're on Windows, then you can either have Visual Studio with the C++ components installed or install their [`Build Tools for Visual Studio`](https://visualstudio.microsoft.com/downloads/?q=build+tools) )*

Alternatively, you can follow the steps below to run the sourcecode!

## Prerequisites

If you're going to run CPPPC from source, then you must have the following dependencies installed:<br>
*(You can also check the requirements.txt...)*

- [cmake](https://cmake.org/)
  - Make sure that you have all dependencies your CMake generator requires.
- Compiler of your choice  
- [python](https://www.python.org/)
- requests
- [PyQt5](https://riverbankcomputing.com/software/pyqt/) (GUI library) 

## Getting Started

To use CPPPC, follow these steps:

1. Install the required prerequisites.

    [Details of prerequisites installation can be found here](docs/REQUIREMENTS.md)

2. Clone the repository:

    ```bash
    git clone https://github.com/lr222gw/CPPPC.git
    ```

3. Navigate to the project directory:

    ```bash
    cd CPPPC
    ```

4. Run the CPPPC tool:

    ```bash
    python cpppc.py
    ```




