# SC4 Python Framework

Write SimCity 4 plugins in Python instead of C++.

## Requirements
- Visual Studio 2022 (MSVC toolchain)
- CMake 3.20+
- Python 3.13+ (lower versions may work, but not tested)
- SimCity 4 Deluxe Edition

## Build
```bash
git clone --recursive <repository-url>
cd sc4-python-wrapper
mkdir build && cd build
cmake .. -G "Visual Studio 17 2022" -A Win32
cmake --build . --config Release
```

## Installation
1. Copy `build/Release/SC4PythonFramework.dll` to `<My Documents>\SimCity 4\Plugins\`
2. Copy the entire `src/python/` directory to `<My Documents>\SimCity 4\PythonScripts\`
3. Download and install a **32-bit (x86) version** of Python (3.13 or higher recommended). From the installation dir, copy python3.dll and python313.dll to the directory in `<Program Files>/SimCity4/Apps` (same directory as SimCity 4.exe)
4. Your plugins go in `<My Documents>\SimCity 4\PythonScripts\<your-plugin-dir>\`

## Setup Dependencies
Run this in the PythonScripts directory to install required packages:
```bash
cd "<My Documents>\SimCity 4\PythonScripts"
uv pip install --target . pydantic
```

## Creating Plugins

### Basic Plugin Structure
```python
from sc4_plugin_base import CheatPlugin
from sc4_types import CheatCommand
from typing import Dict

class MyPlugin(CheatPlugin):
    def get_plugin_info(self) -> Dict[str, str]:
        return {
            "name": "My Plugin",
            "version": "1.0.0",
            "description": "Does something cool",
            "author": "Your Name"
        }
    
    def initialize(self) -> bool:
        self.register_cheat("mycmd", "My custom command")
        return super().initialize()
    
    def process_cheat(self, cheat: CheatCommand) -> bool:
        if cheat.text.lower() == "mycmd":
            print("My command executed!")
            return True
        return False

# Required: plugin instance
plugin_instance = MyPlugin
```

### Plugin Types
- `CheatPlugin`: Handle cheat commands
- `SC4MessagePlugin`: Handle game messages  
- `SC4PluginBase`: Base class for custom behavior

## How it works

C++ DLL loads into SC4 and embeds a Python interpreter. Your plugins run as Python code with access to game data through safe wrapper classes.

## Logging

All output goes to: `<My Documents>\SimCity 4\SC4PythonFramework.log`

Use standard Python logging:
```python
self.logger.info("Something happened")
print("This also appears in the log")
```

## Examples

Example plugins in `PythonScripts/examples/`:
- `logging_demo.py`: Demonstrates logging integration
- `simple_cheat_test.py`: Basic cheat command example

## Technical Details
- 32-bit DLL compatible with SC4's architecture
- Dependencies: gzcom-dll, pybind11, spdlog
- Python packages managed via uv

## Troubleshooting

### Common issues
- **"Python libraries not found"**: Ensure Python 3.13+ is installed
- **"Module not found"**: Run the dependency setup command
- **Plugins not loading**: Check the log file for specific errors

### Debug mode
Build in Debug mode and attach CLion debugger to `SimCity4.exe` process for C++ debugging.
