cmake_minimum_required(VERSION 3.20)

# Force 32-bit build for SimCity 4 compatibility BEFORE project() call
# Set the platform regardless of current setting to ensure 32-bit
set(CMAKE_GENERATOR_PLATFORM "Win32")
message(STATUS "Forcing 32-bit build for SC4 compatibility")

# Force release runtime BEFORE project() call - this is critical
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDLL")
set(CMAKE_CXX_FLAGS_DEBUG "/MD /Zi /Ob0 /Od")
set(CMAKE_C_FLAGS_DEBUG "/MD /Zi /Ob0 /Od")

# Additional 32-bit enforcement
if(WIN32)
    set(CMAKE_SIZEOF_VOID_P 4)
    set(CMAKE_C_SIZEOF_DATA_PTR 4)
    set(CMAKE_CXX_SIZEOF_DATA_PTR 4)
endif()

project(SC4PythonFramework VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Platform specific settings
if(WIN32)
    # set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
    add_definitions(-DWIN32 -D_WINDOWS -DUNICODE -D_UNICODE)
endif()

# MSVC specific settings
if(MSVC)
    add_compile_options(/W4 /permissive-)
    add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
    
    # Force release runtime for all configurations
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDLL")
    
    # Override debug flags to use release runtime
    set(CMAKE_CXX_FLAGS_DEBUG "/MD /Zi /Ob0 /Od /RTC1")
    set(CMAKE_C_FLAGS_DEBUG "/MD /Zi /Ob0 /Od /RTC1")
    
    # Enable debugging in release builds
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Zi")
    set(CMAKE_SHARED_LINKER_FLAGS_RELEASE "${CMAKE_SHARED_LINKER_FLAGS_RELEASE} /DEBUG /OPT:REF /OPT:ICF")
endif()

# Find 32-bit Python 3.13.7 installation
find_program(Python3_EXECUTABLE
    NAMES python python3
    PATHS "D:/Python3137-32" "D:/Python3137-32/Scripts"
    NO_DEFAULT_PATH
)

if(NOT Python3_EXECUTABLE)
    message(FATAL_ERROR "Could not find 32-bit Python 3.13.7 at D:/Python3137-32")
endif()

message(STATUS "Found 32-bit Python executable: ${Python3_EXECUTABLE}")

# Now find the proper 32-bit Python development libraries
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

add_subdirectory(vendor/pybind11)
add_subdirectory(vendor/spdlog)

# gzcom-dll doesn't have CMakeLists.txt, so we include it directly
set(GZCOM_INCLUDE_DIR ${CMAKE_SOURCE_DIR}/vendor/gzcom-dll/gzcom-dll/include)
set(GZCOM_SOURCE_DIR ${CMAKE_SOURCE_DIR}/vendor/gzcom-dll/gzcom-dll/src)

# Automatically find all gzcom-dll source files, excluding main.cpp
file(GLOB GZCOM_SOURCES "${GZCOM_SOURCE_DIR}/*.cpp")
file(GLOB GZCOM_HEADERS "${GZCOM_INCLUDE_DIR}/*.h")

list(REMOVE_ITEM GZCOM_SOURCES
        "${GZCOM_SOURCE_DIR}/main.cpp"
        "${GZCOM_SOURCE_DIR}/cGZCityHallUpgradeDllDirector.cpp"
        "${GZCOM_SOURCE_DIR}/cGZCustomDllDirector.cpp"
        "${GZCOM_SOURCE_DIR}/cGZExampleDllDirector.cpp"
        "${GZCOM_SOURCE_DIR}/cGZExtraCheatsDllDirector.cpp"
        "${GZCOM_SOURCE_DIR}/cGZExtraExtraCheatsDllDirector.cpp"
)
list(APPEND GZCOM_SOURCES
        "${GZCOM_SOURCE_DIR}/cRZCOMDllDirector.cpp "
)

# Include directories - MINIMAL VERSION
include_directories(
    ${CMAKE_SOURCE_DIR}/src/cpp
    ${GZCOM_INCLUDE_DIR}
    # ${Python3_INCLUDE_DIRS}  # COMMENTED OUT
)

# Our source files
set(SOURCES
        src/cpp/PythonFrameworkDllDirector.cpp
        src/cpp/wrappers/CityWrapper.cpp
        src/cpp/python/PythonManager.cpp
        src/cpp/python/PythonBindings.cpp
        src/cpp/utils/Logger.cpp
        ${GZCOM_SOURCES}  # Include all gzcom-dll sources automatically
)

set(HEADERS
    src/cpp/wrappers/CityWrapper.h
    src/cpp/python/PythonManager.h
    src/cpp/utils/Logger.h
    ${GZCOM_HEADERS}  # Include all gzcom-dll headers for IDE support
)

# Create the main DLL with explicit exports
add_library(${PROJECT_NAME} SHARED ${SOURCES} ${HEADERS} SC4PythonFramework.def)

# Link libraries
target_link_libraries(${PROJECT_NAME}
    PRIVATE
    pybind11::embed
    spdlog::spdlog
    ${Python3_LIBRARIES}
)

# set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

# Windows-specific libraries
if(WIN32)
    target_link_libraries(${PROJECT_NAME} PRIVATE kernel32 user32)
endif()

# Set output properties
set_target_properties(${PROJECT_NAME} PROPERTIES
    OUTPUT_NAME "SC4PythonFramework"
    SUFFIX ".dll"
    PREFIX ""
)

# Force Release runtime even in Debug builds to avoid debug runtime dependency issues
if(MSVC)
    set_target_properties(${PROJECT_NAME} PROPERTIES
        MSVC_RUNTIME_LIBRARY "MultiThreadedDLL"
    )
endif()

# Automatic deployment to SC4 directories
if(WIN32)
    # Try to find SC4 installation directory
    set(SC4_INSTALL_PATHS
        "C:/Program Files (x86)/SimCity 4 Deluxe Edition"
        "C:/Program Files (x86)/Maxis/SimCity 4 Deluxe"
        "C:/Program Files/Maxis/SimCity 4 Deluxe"
        "C:/Program Files (x86)/Steam/steamapps/common/SimCity 4 Deluxe"
        "C:/Program Files/Steam/steamapps/common/SimCity 4 Deluxe"
    )
    
    foreach(SC4_PATH ${SC4_INSTALL_PATHS})
        if(EXISTS "${SC4_PATH}/Apps/SimCity 4.exe")
            set(SC4_INSTALL_DIR "${SC4_PATH}")
            break()
        endif()
    endforeach()
    
    # Get user's Documents folder
    set(USERPROFILE_DIR "$ENV{USERPROFILE}")
    set(SC4_PLUGINS_DIR "${USERPROFILE_DIR}/Documents/SimCity 4/Plugins")
    
    if(SC4_INSTALL_DIR)
        message(STATUS "Found SC4 installation at: ${SC4_INSTALL_DIR}")
        
        # Copy Python DLLs to SC4/Apps directory
        set(PYTHON_DIR "D:/Python3137-32")
        set(PYTHON_DLLS 
            "${PYTHON_DIR}/python313.dll"
            "${PYTHON_DIR}/python3.dll"
            "${PYTHON_DIR}/vcruntime140.dll"
        )
        
        foreach(DLL_PATH ${PYTHON_DLLS})
            if(EXISTS ${DLL_PATH})
                add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
                    COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    ${DLL_PATH}
                    "${SC4_INSTALL_DIR}/Apps/"
                    COMMENT "Deploying Python DLL to SC4: ${DLL_PATH}"
                )
            endif()
        endforeach()
        
        # Copy main DLL to user's Plugins folder
        add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E make_directory "${SC4_PLUGINS_DIR}"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
            $<TARGET_FILE:${PROJECT_NAME}>
            "${SC4_PLUGINS_DIR}/"
            COMMENT "Deploying SC4PythonFramework.dll to Plugins folder"
        )
        
        # Set up Python environment and dependencies
        set(PYTHON_SCRIPTS_DIR "${USERPROFILE_DIR}/Documents/SimCity 4/PythonScripts")
        add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
            COMMAND ${Python3_EXECUTABLE} "${CMAKE_SOURCE_DIR}/setup_deps.py"
            COMMENT "Setting up Python environment and dependencies"
        )
        
        message(STATUS "Deployment targets configured:")
        message(STATUS "  - Python DLLs -> ${SC4_INSTALL_DIR}/Apps/")
        message(STATUS "  - SC4PythonFramework.dll -> ${SC4_PLUGINS_DIR}/")
        message(STATUS "  - Python environment -> ${PYTHON_SCRIPTS_DIR}/")
    else()
        message(WARNING "SC4 installation not found. Manual deployment required.")
    endif()
endif()

# Install targets
install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(DIRECTORY src/python/
    DESTINATION PythonScripts
    FILES_MATCHING PATTERN "*.py"
)

install(DIRECTORY docs/
    DESTINATION docs
    FILES_MATCHING PATTERN "*"
)

# Custom target for copying Python files to build directory
add_custom_target(copy_python_files ALL
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_SOURCE_DIR}/src/python
        ${CMAKE_BINARY_DIR}/python
    COMMENT "Copying Python files to build directory"
)

add_dependencies(${PROJECT_NAME} copy_python_files)
