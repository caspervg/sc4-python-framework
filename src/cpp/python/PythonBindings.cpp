#include <pybind11/pybind11.h>
#include <pybind11/embed.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "../wrappers/CityWrapper.h"
#include "../utils/Logger.h"
#include "cIGZMessage2Standard.h"

namespace py = pybind11;

PYBIND11_EMBEDDED_MODULE(sc4_native, m) {
    m.doc() = "SC4 Python Framework Native Bindings";

    // CityWrapper bindings
    py::class_<CityWrapper, std::shared_ptr<CityWrapper>>(m, "CityWrapper")
        .def(py::init<>())
        .def("is_valid", &CityWrapper::IsValid)
        .def("get_city_name", &CityWrapper::GetCityName)
        .def("get_city_population", &CityWrapper::GetCityPopulation)
        .def("get_city_money", &CityWrapper::GetCityMoney)
        .def("set_city_money", &CityWrapper::SetCityMoney)
        .def("add_city_money", &CityWrapper::AddCityMoney)
        .def("get_mayor_mode", &CityWrapper::GetMayorMode)
        .def("set_mayor_mode", &CityWrapper::SetMayorMode)
        .def("get_city_date", &CityWrapper::GetCityDate)
        .def("get_city_time", &CityWrapper::GetCityTime)
        .def("get_city_stats", &CityWrapper::GetCityStats);

    // CityStats structure
    py::class_<CityWrapper::CityStats>(m, "CityStats")
        .def_readonly("residential_population", &CityWrapper::CityStats::residential_population)
        .def_readonly("commercial_population", &CityWrapper::CityStats::commercial_population)
        .def_readonly("industrial_population", &CityWrapper::CityStats::industrial_population)
        .def_readonly("total_jobs", &CityWrapper::CityStats::total_jobs)
        .def_readonly("power_produced", &CityWrapper::CityStats::power_produced)
        .def_readonly("power_consumed", &CityWrapper::CityStats::power_consumed)
        .def_readonly("water_produced", &CityWrapper::CityStats::water_produced)
        .def_readonly("water_consumed", &CityWrapper::CityStats::water_consumed);

    // SC4 Message wrapper (minimal exposure for safety)
    py::class_<cIGZMessage2Standard>(m, "SC4Message")
        .def("get_type", &cIGZMessage2Standard::GetType)
        .def("get_data1", &cIGZMessage2Standard::GetData1)
        .def("get_data2", &cIGZMessage2Standard::GetData2)
        .def("get_data3", &cIGZMessage2Standard::GetData3);

    // Common SC4 message types as constants
    m.attr("MSG_CITY_INIT") = 0x26C63345;
    m.attr("MSG_CITY_SHUTDOWN") = 0x26C63346;
    m.attr("MSG_QUERY_EXEC_START") = 0x26ad8e01;
    m.attr("MSG_QUERY_EXEC_END") = 0x26ad8e02;
    m.attr("MSG_CHEAT_ISSUED") = 0x230E27AC;
    
    // Common cheat codes
    m.attr("CHEAT_FUND") = 0x6990;
    m.attr("CHEAT_POWER") = 0x1DE4F79A;
    m.attr("CHEAT_WATER") = 0x1DE4F79B;
    
    // Logging functions for Python integration
    m.def("log_message", [](const std::string& message, int level) {
        auto logger = Logger::Get();
        if (!logger) return;
        
        switch (level) {
            case 0: logger->debug(message); break;
            case 1: logger->info(message); break;
            case 2: logger->warn(message); break;
            case 3: logger->error(message); break;
            case 4: logger->critical(message); break;
            default: logger->info(message); break;
        }
    }, "Log a message from Python to the C++ logging system",
       py::arg("message"), py::arg("level"));
    
    // Convenience logging functions
    m.def("log_debug", [](const std::string& message) {
        Logger::Get()->debug(message);
    }, "Log a debug message from Python");
    
    m.def("log_info", [](const std::string& message) {
        Logger::Get()->info(message);
    }, "Log an info message from Python");
    
    m.def("log_warn", [](const std::string& message) {
        Logger::Get()->warn(message);
    }, "Log a warning message from Python");
    
    m.def("log_error", [](const std::string& message) {
        Logger::Get()->error(message);
    }, "Log an error message from Python");
    
    m.def("log_critical", [](const std::string& message) {
        Logger::Get()->critical(message);
    }, "Log a critical message from Python");
}