# SC4 Python Framework

A framework for writing SimCity 4 plugins in Python instead of C++. This framework provides safe access to SC4's game engine through a memory-safe C++ wrapper layer, allowing you to create powerful plugins using Python's ecosystem.

## Requirements

- **Windows 10/11** (SimCity 4 platform)
- **Visual Studio 2019/2022** with MSVC toolchain
- **CMake 3.20+**
- **Python 3.13+**
- **SimCity 4 Deluxe Edition**

## Architecture Overview

```
Development Environment (64-bit)           SimCity 4 Runtime (32-bit)
┌─────────────────────────────┐           ┌─────────────────────────────┐
│  Python 3.13+ (64-bit)     │  build    │  SC4PythonFramework.dll     │
│  - Plugin development      │  ──────►  │  - Embedded Python (32-bit)│
│  - Package management      │           │  - GZCOM integration        │
│  - Testing & debugging     │           │  - Plugin execution         │
└─────────────────────────────┘           └─────────────────────────────┘
```

### How It Works
1. **Development**: You write plugins in a modern Python environment
   - Use any packages, libraries, and tools available for Python
   - Develop using your favorite IDE (VS Code, PyCharm, etc.)
2. **Build**: CMake creates a 32-bit DLL with embedded Python
3. **Runtime**: Python runs in SimCity 4's 32-bit address space
4. **Plugin Execution**: Your Python code executes within the game process

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/caspervg/sc4-python-framework.git
cd sc4-python-framework
git submodule update --init --recursive
```

### 2. Build the Framework

#### Using CLion:
1. Open project in CLion
2. Configure CMake with:
   - Generator: Visual Studio 17 2022
   - Architecture: Win32 (will auto-detect if needed)
   - Build type: Release

#### Using Command Line:
```bash
mkdir build && cd build

# CMake will automatically configure for 32-bit SC4 compatibility
cmake .. -G "Visual Studio 17 2022"
cmake --build . --config Release
```

### 3. Install to SimCity 4

```bash
# Copy to SimCity 4 Plugins folder
cp build/Release/SC4PythonFramework.dll "C:/Program Files (x86)/Maxis/SimCity 4 Deluxe/Plugins/"
cp -r build/python "C:/Program Files (x86)/Maxis/SimCity 4 Deluxe/Plugins/"
```

### 4. Write Your First Plugin

Create `my_plugin.py` in the plugins/python folder:

```python
from sc4_plugin_base import CheatPlugin

class MyPlugin(CheatPlugin):
    @property
    def name(self) -> str:
        return "My Awesome Plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Does awesome things!"
    
    def initialize(self) -> bool:
        self.register_cheat("awesome", self.do_awesome_thing, "Make the city awesome")
        return super().initialize()
    
    def do_awesome_thing(self) -> None:
        if self.city.is_valid():
            self.city.add_city_money(1000000)
            self.logger.info("Made the city $1M more awesome!")
```

## Development Workflow

### Setting up Development Environment

```bash
# Use your normal Python (64-bit is fine!)
cd src/python/examples
uv sync  # Install development dependencies

# Develop plugins using your favorite tools
code basic_cheats.py  # VS Code, PyCharm, etc.
```

### Building and Testing

```bash
# Build the 32-bit DLL
cmake --build build --config Release

# Test in SimCity 4
```

### Package Management

Use `uv` with your development Python:

```bash
# Add dependencies for your plugins
cd src/python/examples
uv add numpy pandas matplotlib

# The build system ensures compatibility at runtime
```

## Memory safety

1. **Composition over inheritance**: Never inherit from SC4 interfaces
2. **Thin adapters**: Minimal SC4 interface implementations  
3. **Safe boundaries**: Clear separation between "SC4 world" and "Python world"
4. **RAII patterns**: Automatic resource management
5. **Smart pointers**: No raw pointer management

## Building from Source

### Prerequisites

1. **Visual Studio 2022** with C++ development tools
2. **CMake 3.20+** 
3. **Python 3.13+**
4. **Git** for cloning with submodules

### Build Configuration

The build system automatically handles architecture detection:

```bash
# Configure (auto-detects 32-bit requirement for SC4)
cmake -B build -G "Visual Studio 17 2022" -DCMAKE_BUILD_TYPE=Release

# Build 32-bit DLL regardless of host Python
cmake --build build --config Release
```

### Troubleshooting

**"Python libraries not found"**: Install Python development packages
```bash
# Windows
pip install --upgrade pip setuptools wheel
```

**"Architecture warnings"**: Normal when cross-compiling 64→32 bit
```
Building 32-bit DLL for SC4 compatibility (host is 64-bit)
Cross-compiling: 64-bit Python -> 32-bit DLL
```

**"Missing dependencies"**: Update submodules
```bash
git submodule update --init --recursive
```

## Plugin Development

### Base Classes

- `SC4PluginBase`: Foundation for all plugins
- `CheatPlugin`: For implementing cheat codes  
- `CityAnalysisPlugin`: For analyzing city data
- `EventPlugin`: For responding to game events

### City Data Access

```python
# Safe city data access
city_name = self.city.get_city_name()
population = self.city.get_city_population() 
money = self.city.get_city_money()

# Modify city (safe operations only)
self.city.set_city_money(1000000)
self.city.add_city_money(50000)
self.city.set_mayor_mode(True)

# Get detailed statistics
stats = self.city.get_city_stats()
print(f"Power: {stats.power_produced}/{stats.power_consumed}")
```

## Debugging

### C++ Debugging

1. Build in Debug mode: `cmake --build build --config Debug`
2. Attach debugger to SimCity4.exe
3. Set breakpoints in C++ wrapper code

### Python Debugging

```python
# Logs appear in both places:
self.logger.info("Debug message")  # SC4 log file
print("Debug output")  # VS Debug output (if attached)
```

Log files location:
- `sc4_python.log` in SimCity 4 directory
- Visual Studio Output window (Debug builds)

## Contributing

1. Fork the repository
2. Test builds target 32-bit automatically
3. Verify compatibility with actual SimCity 4
4. Submit pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- **nsgomez**, **memo**, **0xC0000054** and others for gzcom-dll framework and many decoded headers
- **pybind11** team for seamless Python-C++ integration
- **SimCity 4 modding community** for extensive reverse engineering and keeping the game alive!
