#include "Logger.h"
#include <filesystem>
#include <cstdlib>

std::shared_ptr<spdlog::logger> Logger::s_logger = nullptr;
bool Logger::s_initialized = false;

std::shared_ptr<spdlog::logger> Logger::Get()
{
    if (!s_initialized)
    {
        Initialize();
    }
    return s_logger;
}

void Logger::Initialize()
{
    if (s_initialized && s_logger)
    {
        return;
    }

    try
    {
        // Create multiple sinks: console (MSVC debug output) and file
        std::vector<spdlog::sink_ptr> sinks;
        sinks.push_back(std::make_shared<spdlog::sinks::msvc_sink_mt>());
        
        // Add file sink - write to user's Documents folder where SC4 can find it
        std::string userProfile = std::getenv("USERPROFILE") ? std::getenv("USERPROFILE") : "";
        if (!userProfile.empty())
        {
            std::filesystem::path logDir = std::filesystem::path(userProfile) / "Documents" / "SimCity 4";
            std::filesystem::create_directories(logDir);
            
            std::string logPath = (logDir / "SC4PythonFramework.log").string();
            sinks.push_back(std::make_shared<spdlog::sinks::basic_file_sink_mt>(logPath, false));
        }
        
        s_logger = std::make_shared<spdlog::logger>("SC4PythonFramework", sinks.begin(), sinks.end());
        s_logger->set_level(spdlog::level::debug);
        s_logger->set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%n] [%l] %v");
        s_logger->flush_on(spdlog::level::debug); // Flush on every log message
        
        s_initialized = true;
        
        s_logger->info("SC4PythonFramework logger initialized");
        if (!userProfile.empty())
        {
            std::filesystem::path logDir = std::filesystem::path(userProfile) / "Documents" / "SimCity 4";
            std::string logPath = (logDir / "SC4PythonFramework.log").string();
            s_logger->info("Logging to file: {}", logPath);
        }
    }
    catch (const std::exception& e)
    {
        // Fallback to console-only logging if file creation fails
        auto consoleSink = std::make_shared<spdlog::sinks::msvc_sink_mt>();
        s_logger = std::make_shared<spdlog::logger>("SC4PythonFramework", consoleSink);
        s_logger->set_level(spdlog::level::debug);
        s_logger->error("Failed to initialize file logging: {}", e.what());
        s_initialized = true;
    }
}

void Logger::Shutdown()
{
    if (s_logger)
    {
        s_logger->info("SC4PythonFramework logger shutting down");
        s_logger->flush();
        s_logger.reset();
    }
    s_initialized = false;
}