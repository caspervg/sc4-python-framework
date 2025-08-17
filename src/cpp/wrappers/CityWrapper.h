#pragma once

#include <string>
#include <vector>
#include <cstdint>
#include "cISC4City.h"
#include "cISC4App.h"

class CityWrapper
{
public:
    CityWrapper();
    ~CityWrapper();

    // City information
    bool IsValid() const;
    std::string GetCityName() const;
    uint32_t GetCityPopulation() const;
    uint32_t GetCityMoney() const;
    
    // City modification (safe operations only)
    bool SetCityMoney(uint32_t amount);
    bool AddCityMoney(int32_t amount);
    
    // Mayor mode operations
    bool GetMayorMode() const;
    bool SetMayorMode(bool enabled);
    
    // Date/time
    uint32_t GetCityDate() const; // Returns game date
    uint32_t GetCityTime() const; // Returns game time
    
    // City statistics (read-only)
    struct CityStats
    {
        uint32_t residential_population;
        uint32_t commercial_population;
        uint32_t industrial_population;
        uint32_t total_jobs;
        uint32_t power_produced;
        uint32_t power_consumed;
        uint32_t water_produced;
        uint32_t water_consumed;
    };
    
    CityStats GetCityStats() const;
    
    // Internal - not exposed to Python
    void UpdateCityReference();

private:
    cISC4City* city; // Raw pointer - managed by SC4, we don't own it
    mutable CityStats cachedStats{};
    mutable bool statsCacheValid;
    
    void InvalidateStatsCache();
    void UpdateStatsCache() const;
};