#pragma once

#include <spdlog/spdlog.h>
#include <spdlog/sinks/msvc_sink.h>
#include <spdlog/sinks/basic_file_sink.h>
#include <memory>
#include <string>

class Logger
{
public:
    // Get the singleton instance
    static std::shared_ptr<spdlog::logger> Get();
    
    // Initialize the logger (called once at startup)
    static void Initialize();
    
    // Shutdown the logger (called at exit)
    static void Shutdown();

private:
    static std::shared_ptr<spdlog::logger> s_logger;
    static bool s_initialized;
    
    Logger() = default;
    ~Logger() = default;
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;
};

// Convenience macros for logging
#define LOG_TRACE(...) Logger::Get()->trace(__VA_ARGS__)
#define LOG_DEBUG(...) Logger::Get()->debug(__VA_ARGS__)
#define LOG_INFO(...) Logger::Get()->info(__VA_ARGS__)
#define LOG_WARN(...) Logger::Get()->warn(__VA_ARGS__)
#define LOG_ERROR(...) Logger::Get()->error(__VA_ARGS__)
#define LOG_CRITICAL(...) Logger::Get()->critical(__VA_ARGS__)