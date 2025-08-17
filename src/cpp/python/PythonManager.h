#pragma once

// pybind11 includes MUST be first
#include <pybind11/embed.h>
#include <pybind11/pybind11.h>
namespace py = pybind11;
using namespace py::literals;

// Standard library includes after pybind11
#include <memory>
#include <vector>
#include <string>
#include <unordered_map>
#include <map>
#include "spdlog/logger.h"

#include "../wrappers/CityWrapper.h"

// SC4 includes last
#include "cIGZMessage2.h"
#include "cIGZMessage2Standard.h"

// Forward declaration to avoid circular dependency

class PythonManager
{
public:
    PythonManager();
    ~PythonManager();

    // Lifecycle
    bool Initialize();
    void Shutdown();

    // Plugin management
    bool LoadPlugins();
    void UnloadPlugins();
    bool ReloadPlugins();

    // Message handling
    bool HandleMessage(cIGZMessage2& message);
    bool HandleMessage(uint32_t messageType, cIGZMessage2Standard* pMessage);
    
    // Cheat handling
    bool HandleCheat(uint32_t cheatID, const std::string& cheatText);

    // City events
    bool OnCityInit();
    bool OnCityShutdown();

    // Plugin discovery
    std::vector<std::string> DiscoverPluginFiles() const;
    std::string GetPluginsDirectory() const;

    // Python environment
    bool IsPythonInitialized() const { return pythonInitialized; }

    // Error handling
    std::string GetLastError() const { return lastError; }
    
    // Cheat management
    std::map<std::string, std::string> GetRegisteredCheats() const;

private:
    // Python environment
    bool pythonInitialized;
    std::unique_ptr<py::scoped_interpreter> interpreter;

    // CRITICAL: NO py::object members in header! 
    // Python objects can only exist AFTER interpreter is initialized.
    // We'll create these dynamically in Initialize() and destroy in Shutdown().

    // Plugin management - using pointers to avoid Python object members
    struct PluginInfo
    {
        std::string filepath;
        std::string name;
        void* instance_ptr;  // Will cast to py::object* when needed
        bool loaded;
    };
    
    std::unordered_map<std::string, PluginInfo> loadedPlugins;
    std::shared_ptr<CityWrapper> cityWrapper;

    // Error tracking
    mutable std::string lastError;

    // Internal methods
    bool InitializePythonEnvironment();
    bool SetupPythonPaths();
    bool SetupPythonEnvironment();
    bool LoadPythonBootstrap();
    bool SetupPythonLogging();
    bool CreateCityWrapper();

    bool LoadPlugin(const std::string& filepath);
    void UnloadPlugin(const std::string& pluginName);
    
    void SetError(const std::string& error) const;
    void LogMessage(const std::string& message, int level = 0) const;

    // Python callback handlers - no py::args in header!
    bool CallPluginMethod(const std::string& pluginName, const std::string& method);
    bool CallAllPlugins(const std::string& method);
};