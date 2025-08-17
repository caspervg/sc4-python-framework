#include "python/PythonManager.h"
#include "utils/Logger.h"
#include "cRZMessage2COMDirector.h"
#include "cIGZMessage2Standard.h"
#include "cIGZFrameWork.h"
#include "cIGZApp.h"
#include "cIGZCheatCodeManager.h"
#include "cIGZMessageServer2.h"
#include "cISC4App.h"
#include "cRZBaseString.h"
#include "GZServPtrs.h"
#include <memory>
#include <windows.h>


static const uint32_t kPythonPluginDirectorID = 0x00fd9a21;

// SC4 GUIDs
static const uint32_t kGZIID_cIGZCheatCodeManager = 0xa1085722;
static const uint32_t kGZIID_cISC4App = 0x26ce01c0;

// SC4 Message IDs
static const uint32_t kGZMSG_CheatIssued = 0x230e27ac;
static const uint32_t kMsgCityInit = 0x26C63345;
static const uint32_t kMsgCityShutdown = 0x26C63346;
static const uint32_t kMsgQueryExecStart = 0x26ad8e01;
static const uint32_t kMsgQueryExecEnd = 0x26ad8e02;


class PythonFrameworkDllDirector final : public cRZMessage2COMDirector
{
public:
    PythonFrameworkDllDirector() : cheatManager(nullptr)
    {
        Logger::Initialize();
        LOG_INFO("PythonFrameworkDllDirector constructor called");
    }

    virtual ~PythonFrameworkDllDirector()
    {
        LOG_INFO("PythonFrameworkDllDirector destructor called");
        Logger::Shutdown();
    }

    uint32_t GetDirectorID() const override
    {
        return kPythonPluginDirectorID;
    }
    
    bool OnStart(cIGZCOM* pCOM) override
    {
        (void)pCOM; // Unused parameter
        LOG_INFO("OnStart() called");

        // Create PythonManager here (deferred initialization)
        LOG_INFO("Creating PythonManager instance...");
        pythonManager = std::make_unique<PythonManager>();
        LOG_INFO("PythonManager created successfully");

        mpFrameWork->AddHook(this);
        return true;
    }

    bool PreAppInit() override
    {
        LOG_INFO("PreAppInit() called - deferring Python init to PostAppInit");
        // Defer Python initialization to PostAppInit to ensure all DLLs are loaded
        return true;
    }

    bool PostAppInit() override
    {
        LOG_INFO("PostAppInit() called");
        if (!pythonManager) {
            LOG_ERROR("PostAppInit() called but PythonManager not created");
            return false;
        }
        
        // Get and register with the cheat manager
        if (!SetupCheatManager()) {
            LOG_WARN("Failed to setup cheat manager integration");
        }
        
        // Initialize Python environment first
        if (!pythonManager->Initialize()) {
            LOG_ERROR("Failed to initialize Python environment");
            return false;
        }
        
        // Then load plugins
        bool result = pythonManager->LoadPlugins();
        
        // Register Python plugin cheats with SC4
        RegisterPythonCheats();
        
        // Register for city messages
        cIGZMessageServer2Ptr pMsgServ;
        if (pMsgServ) {
            pMsgServ->AddNotification(this, kMsgCityInit);
            pMsgServ->AddNotification(this, kMsgCityShutdown);
            LOG_INFO("Registered for city initialization messages");
        } else {
            LOG_WARN("Failed to get message server for city notifications");
        }
        
        LOG_INFO("PostAppInit() completed successfully");
        return result;
    }

    bool PreAppShutdown() override
    {
        LOG_INFO("PreAppShutdown() called");
        if (pythonManager) {
            pythonManager->UnloadPlugins();
        }
        LOG_INFO("PreAppShutdown() completed");
        return true;
    }

    bool PostAppShutdown() override
    {
        LOG_INFO("PostAppShutdown() called");
        if (pythonManager) {
            pythonManager->Shutdown();
        }
        LOG_INFO("PostAppShutdown() completed");
        return true;
    }

    bool DoMessage(cIGZMessage2* pMessage) override
    {
        if (!pMessage) {
            return false;
        }

        uint32_t messageType = pMessage->GetType();
        
        if (messageType == kGZMSG_CheatIssued) {
            try {
                LOG_INFO("Cheat message received");
                // Use static_cast instead of dynamic_cast to avoid RTTI issues
                const auto* pStandardMsg = static_cast<cIGZMessage2Standard*>(pMessage);
                
                const uint32_t dwCheatID = pStandardMsg->GetData1();
                const auto* pszCheatData = static_cast<cIGZString*>(pStandardMsg->GetVoid2());
                
                // Only process cheats that we registered
                std::string cheatText;
                if (pszCheatData && pszCheatData->ToChar()) {
                    cheatText = pszCheatData->ToChar();
                }
                
                LOG_INFO("Cheat ID: 0x{:08x}, Text: '{}'", dwCheatID, cheatText);
                
                if (!pythonManager) {
                    LOG_ERROR("PythonManager is null");
                    return true;
                }
                
                // Check if this is one of our Python cheats
                LOG_INFO("Getting registered cheats");
                auto pythonCheats = pythonManager->GetRegisteredCheats();
                LOG_INFO("Got {} registered cheats", pythonCheats.size());
                
                bool isPythonCheat = pythonCheats.find(cheatText) != pythonCheats.end();
                
                if (isPythonCheat) {
                    LOG_INFO("Processing Python cheat: '{}'", cheatText);
                    ProcessCheat(dwCheatID, pszCheatData);
                } else {
                    LOG_DEBUG("Ignoring non-Python cheat: '{}'", cheatText);
                }
            } catch (const std::exception& e) {
                LOG_ERROR("Exception in cheat processing: {}", e.what());
            } catch (...) {
                LOG_ERROR("Unknown exception in cheat processing");
            }
        }
        else if (messageType == kMsgCityInit) {
            LOG_INFO("Processing city initialization message");
            if (pythonManager) {
                pythonManager->OnCityInit();
            }
        }
        else if (messageType == kMsgCityShutdown) {
            LOG_INFO("Processing city shutdown message");
            if (pythonManager) {
                pythonManager->OnCityShutdown();
            }
        }

        return true;
    }

private:
    std::unique_ptr<PythonManager> pythonManager;
    cIGZCheatCodeManager* cheatManager;
    
    bool SetupCheatManager()
    {
        cIGZFrameWork* const pFramework = RZGetFrameWork();
        if (!pFramework) {
            LOG_ERROR("Failed to get framework");
            return false;
        }
        
        cIGZApp* const pApp = pFramework->Application();
        if (!pApp) {
            LOG_ERROR("Failed to get application");
            return false;
        }
        
        cISC4App* pISC4App;
        if (!pApp->QueryInterface(kGZIID_cISC4App, (void**)&pISC4App)) {
            LOG_ERROR("Failed to get SC4 application interface");
            return false;
        }
        
        cheatManager = pISC4App->GetCheatCodeManager();
        if (!cheatManager) {
            LOG_ERROR("Failed to get cheat code manager");
            return false;
        }
        
        // Register ourselves as a notification target for cheat messages
        if (!cheatManager->AddNotification2(this, 0)) {
            LOG_WARN("Failed to register for cheat notifications");
        }
        
        LOG_INFO("Cheat manager setup completed successfully");
        return true;
    }
    
    void RegisterPythonCheats()
    {
        if (!cheatManager || !pythonManager) {
            return;
        }
        
        // Get list of registered cheats from Python plugins
        auto pythonCheats = pythonManager->GetRegisteredCheats();
        
        for (const auto& [cheatText, cheatInfo] : pythonCheats) {
            uint32_t cheatID = std::hash<std::string>{}(cheatText); // Generate ID from text
            cRZBaseString cheatName(cheatText.c_str());
            
            if (cheatManager->RegisterCheatCode(cheatID, cheatName)) {
                LOG_INFO("Registered Python cheat: '{}' with ID 0x{:08x}", cheatText, cheatID);
            } else {
                LOG_WARN("Failed to register Python cheat: '{}'", cheatText);
            }
        }
    }

    bool ProcessCheat(uint32_t dwCheatID, cIGZString const* szCheatText)
    {
        if (!pythonManager) {
            LOG_WARN("ProcessCheat called but PythonManager not available");
            return false;
        }

        // Convert cIGZString to std::string
        std::string cheatText;
        if (szCheatText && szCheatText->ToChar()) {
            cheatText = szCheatText->ToChar();
        }

        LOG_INFO("ProcessCheat called - ID: 0x{:08x}, Text: '{}'", dwCheatID, cheatText);
        
        // Forward to Python manager
        return pythonManager->HandleCheat(dwCheatID, cheatText);
    }
};

// Required export - gzcom-dll will call this
cRZCOMDllDirector* RZGetCOMDllDirector()
{
    static PythonFrameworkDllDirector sDirector;
    
    // Note: Can't use g_logger here since it may not be initialized yet
    OutputDebugStringA("[SC4PythonFramework] RZGetCOMDllDirector() called\n");
    return &sDirector;
}