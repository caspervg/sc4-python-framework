// pybind11 includes MUST be first - included via PythonManager.h
#include "PythonManager.h"

// Other includes after pybind11
#include "../wrappers/CityWrapper.h"
#include "../utils/Logger.h"
#include "cIGZMessage2.h"
#include <filesystem>
#include <fstream>
#include <windows.h>


PythonManager::PythonManager()
{
    this->pythonInitialized = false;
    this->cityWrapper = std::make_unique<CityWrapper>();
}

PythonManager::~PythonManager()
{
    LOG_INFO("PythonManager destructor called");
    Shutdown();
}

bool PythonManager::Initialize()
{
    if (pythonInitialized)
    {
        LOG_INFO("Python already initialized");
        return true;
    }

    try
    {
        LOG_INFO("Initializing Python interpreter...");
        
        // Initialize interpreter - this must persist for the lifetime of the object
        interpreter = std::make_unique<py::scoped_interpreter>();
        LOG_INFO("Python interpreter initialized successfully");

        // Import the native sc4_native module to make it available to Python
        try {
            py::module sc4_native = py::module::import("sc4_native");
            LOG_INFO("sc4_native module imported successfully");
        } catch (const std::exception& e) {
            LOG_ERROR("Failed to import sc4_native module: {}", e.what());
            SetError("Failed to import native module");
            return false;
        }

        if (!SetupPythonPaths())
        {
            SetError("Failed to setup Python paths");
            return false;
        }
        
        if (!SetupPythonEnvironment())
        {
            LOG_WARN("Failed to setup Python environment, proceeding with basic functionality");
        }

        if (!LoadPythonBootstrap())
        {
            SetError("Failed to load Python bootstrap code");
            return false;
        }
        
        // Set up Python logging integration
        if (!SetupPythonLogging())
        {
            LOG_WARN("Failed to setup Python logging integration, proceeding anyway");
        }

        pythonInitialized = true;
        LOG_INFO("Python environment initialized successfully");
        return true;
    }
    catch (const std::exception& e)
    {
        SetError("Python initialization failed: " + std::string(e.what()));
        LOG_ERROR("Exception during Python initialization: {}", e.what());
        return false;
    }
}

void PythonManager::Shutdown()
{
    if (!pythonInitialized) return;

    try
    {
        LOG_INFO("Starting Python shutdown sequence...");
        
        // Unload all plugins first
        UnloadPlugins();
        
        // Destroy interpreter (automatically handled by scoped_interpreter destructor)
        LOG_INFO("Shutting down Python interpreter...");
        interpreter.reset();
        
        pythonInitialized = false;
        LOG_INFO("Python environment shut down successfully");
    }
    catch (const std::exception& e)
    {
        LOG_ERROR("Error during Python shutdown: {}", e.what());
    }
}

bool PythonManager::LoadPlugins()
{
    if (!pythonInitialized)
    {
        SetError("Python not initialized");
        return false;
    }

    try
    {
        auto pluginFiles = DiscoverPluginFiles();
        LOG_INFO("Found {} plugin files", pluginFiles.size());

        bool allLoaded = true;
        for (const auto& filepath : pluginFiles)
        {
            if (!LoadPlugin(filepath))
            {
                LOG_WARN("Failed to load plugin: {}", filepath);
                allLoaded = false;
            }
        }

        return allLoaded;
    }
    catch (const std::exception& e)
    {
        SetError("Failed to load plugins: " + std::string(e.what()));
        return false;
    }
}

void PythonManager::UnloadPlugins()
{
    try
    {
        for (auto& [name, plugin] : loadedPlugins)
        {
            if (plugin.loaded && plugin.instance_ptr)
            {
                CallPluginMethod(name, "shutdown");
                
                // Clean up the py::object pointer
                delete static_cast<py::object*>(plugin.instance_ptr);
                plugin.instance_ptr = nullptr;
                plugin.loaded = false;
            }
        }
        loadedPlugins.clear();
        LOG_INFO("All plugins unloaded");
    }
    catch (const std::exception& e)
    {
        LOG_ERROR("Error unloading plugins: {}", e.what());
    }
}

bool PythonManager::ReloadPlugins()
{
    UnloadPlugins();
    return LoadPlugins();
}

// Simplified implementations without py::args for now
bool PythonManager::CallPluginMethod(const std::string& pluginName, const std::string& method)
{
    auto it = loadedPlugins.find(pluginName);
    if (it == loadedPlugins.end() || !it->second.loaded || !it->second.instance_ptr)
    {
        return false;
    }

    try
    {
        auto* plugin = static_cast<py::object*>(it->second.instance_ptr);
        if (py::hasattr(*plugin, method.c_str()))
        {
            plugin->attr(method.c_str())();
        }
        return true;
    }
    catch (const std::exception& e)
    {
        LOG_ERROR("Error calling {} on {}: {}", method, pluginName, e.what());
        return false;
    }
}

bool PythonManager::CallAllPlugins(const std::string& method)
{
    bool allSucceeded = true;
    for (const auto& [name, plugin] : loadedPlugins)
    {
        if (plugin.loaded)
        {
            if (!CallPluginMethod(name, method))
            {
                allSucceeded = false;
            }
        }
    }
    return allSucceeded;
}

bool PythonManager::HandleMessage(cIGZMessage2& message)
{
    if (!pythonInitialized) return true;
    
    LOG_DEBUG("HandleMessage called");
    return true;
}

bool PythonManager::HandleMessage(uint32_t messageType, cIGZMessage2Standard* pMessage)
{
    if (!pythonInitialized) return false;
    
    LOG_DEBUG("HandleMessage with type 0x{:08x} called", messageType);
    
    try {
        // Import SC4Message from sc4_types
        py::module sc4_types = py::module::import("sc4_types");
        py::object SC4Message = sc4_types.attr("SC4Message");
        
        // Create an SC4Message object
        py::dict messageArgs;
        messageArgs["message_type"] = messageType;
        if (pMessage) {
            messageArgs["data1"] = pMessage->GetData1();
            messageArgs["data2"] = pMessage->GetData2();
            messageArgs["data3"] = pMessage->GetData3();
        }
        
        py::object sc4Message = SC4Message(**messageArgs);
        
        // Forward message to all loaded plugins
        for (const auto& [pluginName, plugin] : loadedPlugins) {
            if (plugin.loaded && plugin.instance_ptr) {
                auto* pluginObj = static_cast<py::object*>(plugin.instance_ptr);
                if (py::hasattr(*pluginObj, "handle_message")) {
                    py::object result = pluginObj->attr("handle_message")(sc4Message);
                    // If plugin returns True, it handled the message
                    if (result.cast<bool>()) {
                        LOG_DEBUG("Message 0x{:08x} handled by plugin: {}", messageType, pluginName);
                    }
                }
            }
        }
        return true;
        
    } catch (const std::exception& e) {
        LOG_ERROR("Error handling message 0x{:08x}: {}", messageType, e.what());
        return false;
    }
}

bool PythonManager::HandleCheat(uint32_t cheatID, const std::string& cheatText)
{
    if (!pythonInitialized) {
        LOG_WARN("HandleCheat called but Python not initialized");
        return false;
    }
    
    LOG_INFO("HandleCheat called - ID: 0x{:08x}, Text: '{}'", cheatID, cheatText);
    
    try {
        // Import CheatCommand from sc4_types
        py::module sc4_types = py::module::import("sc4_types");
        py::object CheatCommand = sc4_types.attr("CheatCommand");
        
        // Create a CheatCommand object
        py::object cheatCommand = CheatCommand(
            py::arg("cheat_id") = cheatID,
            py::arg("text") = cheatText
        );
        
        // Call all plugins with the CheatCommand object
        for (const auto& [pluginName, plugin] : loadedPlugins) {
            if (plugin.loaded && plugin.instance_ptr) {
                auto* pluginObj = static_cast<py::object*>(plugin.instance_ptr);
                if (py::hasattr(*pluginObj, "handle_cheat")) {
                    py::object result = pluginObj->attr("handle_cheat")(cheatCommand);
                    // If any plugin handles the cheat and returns True, consider it processed
                    if (result.cast<bool>()) {
                        LOG_INFO("Cheat '{}' handled by plugin: {}", cheatText, pluginName);
                        return true;
                    }
                }
            }
        }
        
        // If no plugin handled it, log that it was unhandled
        LOG_DEBUG("Cheat '{}' not handled by any loaded plugins", cheatText);
        return false;
        
    } catch (const std::exception& e) {
        LOG_ERROR("Error processing cheat '{}': {}", cheatText, e.what());
        return false;
    }
}

bool PythonManager::OnCityInit()
{
    if (!pythonInitialized) return true;

    try
    {
        cityWrapper->UpdateCityReference();
        return CallAllPlugins("on_city_init");
    }
    catch (const std::exception& e)
    {
        LOG_ERROR("Error in city init: {}", e.what());
        return true;
    }
}

bool PythonManager::OnCityShutdown()
{
    if (!pythonInitialized) return true;

    try
    {
        return CallAllPlugins("on_city_shutdown");
    }
    catch (const std::exception& e)
    {
        LOG_ERROR("Error in city shutdown: {}", e.what());
        return true;
    }
}

std::vector<std::string> PythonManager::DiscoverPluginFiles() const
{
    std::vector<std::string> pluginFiles;
    std::string pluginsDir = GetPluginsDirectory();

    try
    {
        if (!std::filesystem::exists(pluginsDir))
        {
            LOG_WARN("Plugins directory does not exist: {}", pluginsDir);
            return pluginFiles;
        }

        for (const auto& entry : std::filesystem::directory_iterator(pluginsDir))
        {
            if (entry.is_regular_file() && entry.path().extension() == ".py")
            {
                std::string filename = entry.path().filename().string();
                if (filename[0] != '_')
                {
                    pluginFiles.push_back(entry.path().string());
                }
            }
        }
    }
    catch (const std::exception& e)
    {
        LOG_ERROR("Error discovering plugins: {}", e.what());
    }

    return pluginFiles;
}

std::string PythonManager::GetPluginsDirectory() const
{
    HMODULE hModule = GetModuleHandleA("SC4PythonFramework.dll");
    if (!hModule) hModule = GetModuleHandleA(nullptr);
    
    char modulePath[MAX_PATH];
    GetModuleFileNameA(hModule, modulePath, MAX_PATH);
    
    std::filesystem::path dllPath(modulePath);
    // Go up one level from Plugins folder to SimCity 4 folder, then into PythonScripts
    std::filesystem::path pythonScriptsPath = dllPath.parent_path().parent_path() / "PythonScripts";
    
    return pythonScriptsPath.string();
}

bool PythonManager::SetupPythonPaths()
{
    try
    {
        py::module sys = py::module::import("sys");
        py::list path = sys.attr("path");
        
        std::string scriptsDir = GetPluginsDirectory();
        path.insert(0, scriptsDir);
        
        LOG_INFO("Added Python path: {}", scriptsDir);
        return true;
    }
    catch (const std::exception& e)
    {
        SetError("Failed to setup Python paths: " + std::string(e.what()));
        return false;
    }
}

bool PythonManager::SetupPythonEnvironment()
{
    try
    {
        LOG_INFO("Setting up Python environment...");
        
        std::string scriptsDir = GetPluginsDirectory();
        py::module sys = py::module::import("sys");
        py::list path = sys.attr("path");
        
        // Check if packages were installed directly in the scripts directory
        // Look for pydantic as an indicator that dependencies are installed
        std::filesystem::path pydanticPath = std::filesystem::path(scriptsDir) / "pydantic";
        
        if (std::filesystem::exists(pydanticPath)) {
            LOG_INFO("Found Python packages installed in: {}", scriptsDir);
            // The scriptsDir is already in path from SetupPythonPaths(), 
            // so packages should be found automatically
        } else {
            LOG_WARN("Python packages not found. Run setup_deps.py to install dependencies.");
        }
        
        return true;
        
    } catch (const std::exception& e) {
        LOG_ERROR("Error setting up Python environment: {}", e.what());
        return false;
    }
}

bool PythonManager::LoadPythonBootstrap()
{
    try
    {
        py::module pluginLoader = py::module::import("plugin_loader");
        LOG_INFO("Plugin loader module imported successfully");
        return true;
    }
    catch (const std::exception& e)
    {
        SetError("Failed to load plugin loader: " + std::string(e.what()));
        return false;
    }
}

bool PythonManager::SetupPythonLogging()
{
    try
    {
        py::module sc4_logger = py::module::import("sc4_logger");
        py::object setup_function = sc4_logger.attr("setup_python_logging");
        setup_function();
        
        LOG_INFO("Python logging integration initialized successfully");
        return true;
    }
    catch (const std::exception& e)
    {
        LOG_ERROR("Failed to setup Python logging: {}", e.what());
        return false;
    }
}

bool PythonManager::LoadPlugin(const std::string& filepath)
{
    try
    {
        std::filesystem::path path(filepath);
        std::string pluginName = path.stem().string();

        if (loadedPlugins.find(pluginName) != loadedPlugins.end())
        {
            LOG_INFO("Plugin already loaded: {}", pluginName);
            return true;
        }

        // TODO: Use plugin loader class once it's properly initialized
        // For now, directly import the plugin module
        py::module pluginModule = py::module::import(pluginName.c_str());
        
        // TODO: Instantiate plugin class and call initialize
        // py::object pluginInstance = pluginModule.attr("Plugin")(cityWrapper);

        PluginInfo info;
        info.filepath = filepath;
        info.name = pluginName;
        info.instance_ptr = nullptr;  // TODO: Store plugin instance
        info.loaded = true;

        loadedPlugins[pluginName] = info;

        // CallPluginMethod(pluginName, "initialize");

        LOG_INFO("Loaded plugin: {}", pluginName);
        return true;
    }
    catch (const std::exception& e)
    {
        SetError("Failed to load plugin " + filepath + ": " + std::string(e.what()));
        return false;
    }
}

void PythonManager::UnloadPlugin(const std::string& pluginName)
{
    auto it = loadedPlugins.find(pluginName);
    if (it != loadedPlugins.end())
    {
        try
        {
            CallPluginMethod(pluginName, "shutdown");

            if (it->second.instance_ptr)
            {
                delete static_cast<py::object*>(it->second.instance_ptr);
                it->second.instance_ptr = nullptr;
            }

            it->second.loaded = false;
            loadedPlugins.erase(it);
            LOG_INFO("Unloaded plugin: {}", pluginName);
        }
        catch (const std::exception& e)
        {
            LOG_ERROR("Error unloading plugin {}: {}", pluginName, e.what());
        }
    }
}

void PythonManager::SetError(const std::string& error) const
{
    lastError = error;
    LOG_ERROR("{}", error);
}