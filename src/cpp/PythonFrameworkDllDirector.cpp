#include "python/PythonManager.h"
#include "utils/Logger.h"
#include "cRZMessage2COMDirector.h"
#include "cIGZMessage2Standard.h"
#include "cIGZFrameWork.h"
#include "cIGZCheatCodeManager.h"
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
        
        // Initialize Python environment first
        if (!pythonManager->Initialize()) {
            LOG_ERROR("Failed to initialize Python environment");
            return false;
        }
        
        // Then load plugins
        bool result = pythonManager->LoadPlugins();
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
            LOG_INFO("Processing cheat message");
            const auto* pStandardMsg = dynamic_cast<cIGZMessage2Standard*>(pMessage);
            const uint32_t dwCheatID = pStandardMsg->GetData1();
            const auto* pszCheatData = static_cast<cIGZString*>(pStandardMsg->GetVoid2());
            
            ProcessCheat(dwCheatID, pszCheatData);
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