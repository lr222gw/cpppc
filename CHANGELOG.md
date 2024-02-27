# Release Notes - Version 0.2.0

## Summary

This release introduces several new features, improvements, and bug fixes to enhance the overall functionality and user experience of the project. The changes include updates to the GUI, refactoring of code, bug fixes, and additional functionalities related to library management, CMake configuration, and more.

## Changes

### Added
- Creation of dummy CMake project to find library path
- Execution of dummy CMake projects and collecting of library specific data
- Parsing of CMake based Libraries
- Parsing of non-cmake based Libraries, tries to create a CMakeLists.txt (Experimental)
- Added Fetcher for projects hosted on GitHub.
- Added GUI window for configuration of libraries
- Added support for specifying include keywords to `TargetDatas`.
- Added support for specifying link targets to `TargetDatas`.
- Users can now define which components to use for libraries that uses them.
- Added support for Persistant storage.
- Added caching of library data used to speed up creation process on following executions.
- User specified path to `Local Libraries` directory is stored in Persistance Storage
- Warning popup is displayed if CMake is missing.
- Introduced a `requirements.txt` file for Python, if running CPPPC from source.
- Threading added to handle loading indicators.

### Updated
- Cleaned up `CMakeVersionData` class.
- GenericTypeValueSetterMetaClass moved to its own file.
- Improved parsing of local and Git libraries for fetching targets.
- Replaced pathify with cross-platform `os.path.join`.
- Now using users' CMake version in `cmakeifyLib`.
- Color theme changes and moved theme configuration to `theme.py`.
- CPPPC windows have titles now.

### Fixed
- Warns users instead of crashing if an invalid path is given to a library.
- Fixed default values initialization before usage.
- CMakeLists.txt now follows overwrite rule.
- Libs `TargetDatas` are set for BareBones project as well.
- Fixed issues with white theme on Windows.
- Ensure images in media are bundled with the executable.
- No longer adding include to generated CMake files if not used.
- Removed files generated in library sources during CMake configuration.
- Ignored copy build dirs if they exist in the source when copying local library source.
- Fixed issues where required caused find modules not to be parsed correctly.
- Configuration paths couldn't contain parentheses.
- Improved handling of Hash and file functions.
- `PersistantDataManager` only retrieves `depdat` if its content is not empty.
- All windows will close if the main window is closed.

### Removed
- Extra parsing of library files.
- Old str-based solution to generate CMakeLists.

## Other
- Various other cleanup, refactoring, and improvements have been made throughout the codebase.

# Release Notes - Version 0.1.0
Happy to announce the first (alpha) release of CPPPC (C++ Project Configurator) - version 0.1.0

## Changes

### Added
- Project Initialization: CPPPC can now generate a directory structure and a CMakeLists.txt file for an executable project based on user settings provided through the GUI.
- Cross Platform: Executables are available for Linux, Windows and Mac (only tested on Linux and Windows)
- Basic user configuration: Users can configure some basic settings :
  - Properties:
    - C++ version
    - C++ Compiler Extensions
    - Generating Compile Commands
    - Link what you use
    - Include What you use
    - Interprocedural Optimizations
  - Link/compile options:
    - Sanitizers, address, leak, undef
    - Blacklist
  - CMake to C++ communication:
    - Access data from CMake in C++, such as Project version
  - Other features:
    - Measure compilation time
    - Use CCache


