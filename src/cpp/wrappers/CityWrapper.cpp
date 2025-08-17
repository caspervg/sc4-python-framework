#include "CityWrapper.h"
#include "cISC4City.h"
#include "cISC4App.h"
#include "cISC4BudgetSimulator.h"
#include "cISC4ResidentialSimulator.h"
#include "cISC4PowerSimulator.h"
#include "cISC4PlumbingSimulator.h"
#include "cISC424HourClock.h"
#include "cRZBaseString.h"
#include <algorithm>

CityWrapper::CityWrapper()
    : city(nullptr)
    , statsCacheValid(false)
{
}

CityWrapper::~CityWrapper()
{
    // We don't own the city pointer, so don't delete it
}

bool CityWrapper::IsValid() const
{
    return city != nullptr;
}

std::string CityWrapper::GetCityName() const
{
    if (!IsValid()) return "";
    
    cRZBaseString cityName;
    if (city->GetCityName(cityName))
    {
        // Convert cIGZString to std::string
        const char* nameStr = cityName.ToChar();
        return nameStr ? std::string(nameStr) : "";
    }
    return "";
}

uint32_t CityWrapper::GetCityPopulation() const
{
    if (!IsValid()) return 0;
    
    // Get residential simulator and query population
    cISC4ResidentialSimulator* resSimulator = city->GetResidentialSimulator();
    if (resSimulator)
    {
        // This would need the proper method call to get population
        // return resSimulator->GetTotalPopulation();
    }
    return 0;
}

uint32_t CityWrapper::GetCityMoney() const
{
    if (!IsValid()) return 0;
    
    cISC4BudgetSimulator* budget = city->GetBudgetSimulator();
    if (budget)
    {
        int64_t funds = budget->GetTotalFunds();
        return static_cast<uint32_t>(std::max(0LL, funds));
    }
    return 0;
}

bool CityWrapper::SetCityMoney(uint32_t amount)
{
    if (!IsValid()) return false;
    
    cISC4BudgetSimulator* budget = city->GetBudgetSimulator();
    if (budget)
    {
        return budget->SetTotalFunds(static_cast<int64_t>(amount));
    }
    return false;
}

bool CityWrapper::AddCityMoney(int32_t amount)
{
    if (!IsValid()) return false;
    
    cISC4BudgetSimulator* budget = city->GetBudgetSimulator();
    if (budget)
    {
        if (amount >= 0)
        {
            return budget->DepositFunds(static_cast<int64_t>(amount));
        }
        else
        {
            return budget->WithdrawFunds(static_cast<int64_t>(-amount));
        }
    }
    return false;
}

bool CityWrapper::GetMayorMode() const
{
    if (!IsValid()) return false;
    
    // Query mayor mode from city - this might be in the city state
    return city->IsInCityTimeSimulationMode();
}

bool CityWrapper::SetMayorMode(bool enabled)
{
    if (!IsValid()) return false;
    
    // Toggle simulation mode if current state doesn't match desired state
    bool currentMode = GetMayorMode();
    if (currentMode != enabled)
    {
        city->ToggleSimulationMode();
    }
    return true;
}

uint32_t CityWrapper::GetCityDate() const
{
    if (!IsValid()) return 0;
    
    // Get city birth date as a starting point
    return city->GetBirthDate();
}

uint32_t CityWrapper::GetCityTime() const
{
    if (!IsValid()) return 0;
    
    // Get simulation time from 24-hour clock
    cISC424HourClock* clock = city->Get24HourClock();
    if (clock)
    {
        // This would need proper implementation based on cISC424HourClock interface
        // return clock->GetCurrentTime();
    }
    return 0;
}

CityWrapper::CityStats CityWrapper::GetCityStats() const
{
    if (!statsCacheValid)
    {
        UpdateStatsCache();
    }
    return cachedStats;
}

void CityWrapper::UpdateCityReference()
{
    // Get current city from SC4App
    // This would be called when city changes
    InvalidateStatsCache();
}

void CityWrapper::InvalidateStatsCache()
{
    statsCacheValid = false;
}

void CityWrapper::UpdateStatsCache() const
{
    if (!IsValid())
    {
        cachedStats = {};
        statsCacheValid = true;
        return;
    }
    
    // Query all stats from city and cache them
    cachedStats.residential_population = GetCityPopulation();
    cachedStats.commercial_population = 0;  // Would get from commercial simulator
    cachedStats.industrial_population = 0;  // Would get from industrial simulator
    cachedStats.total_jobs = 0;             // Sum from various simulators
    
    // Power stats
    cISC4PowerSimulator* powerSim = city->GetPowerSimulator();
    if (powerSim)
    {
        // These would need proper method calls based on cISC4PowerSimulator interface
        // cachedStats.power_produced = powerSim->GetTotalPowerProduced();
        // cachedStats.power_consumed = powerSim->GetTotalPowerConsumed();
    }
    
    // Water stats
    cISC4PlumbingSimulator* waterSim = city->GetPlumbingSimulator();
    if (waterSim)
    {
        // These would need proper method calls based on cISC4PlumbingSimulator interface
        // cachedStats.water_produced = waterSim->GetTotalWaterProduced();
        // cachedStats.water_consumed = waterSim->GetTotalWaterConsumed();
    }
    
    statsCacheValid = true;
}