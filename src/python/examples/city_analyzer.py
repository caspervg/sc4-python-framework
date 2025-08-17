"""
City Analyzer Plugin for SC4 Python Framework

This plugin demonstrates how to analyze city data and provide insights.
"""

from sc4_plugin_base import CityAnalysisPlugin
import time
import threading
from typing import Dict, Any

class CityAnalyzerPlugin(CityAnalysisPlugin):
    """
    Plugin that analyzes city data and provides insights.
    """
    
    @property
    def name(self) -> str:
        return "City Analyzer"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Analyzes city data and provides insights about population, finances, and utilities"
    
    @property
    def author(self) -> str:
        return "SC4 Python Framework"
    
    def initialize(self) -> bool:
        """Initialize the plugin."""
        if not super().initialize():
            return False
        
        # Set analysis interval to 30 seconds
        self.analysis_interval = 30.0
        self.running = False
        self.analysis_thread = None
        
        # Store historical data
        self.population_history = []
        self.money_history = []
        self.max_history_size = 100
        
        self.logger.info("City Analyzer initialized")
        return True
    
    def start_analysis(self) -> None:
        """Start periodic city analysis."""
        if self.running:
            return
        
        self.running = True
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        self.logger.info(f"Started city analysis (interval: {self.analysis_interval}s)")
    
    def stop_analysis(self) -> None:
        """Stop periodic city analysis."""
        if not self.running:
            return
        
        self.running = False
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=5.0)
        
        self.logger.info("Stopped city analysis")
    
    def _analysis_loop(self) -> None:
        """Main analysis loop that runs in a separate thread."""
        while self.running:
            try:
                if self.city.is_valid():
                    analysis_results = self.analyze_city()
                    self._process_analysis_results(analysis_results)
                
                # Sleep in small chunks to allow for responsive shutdown
                elapsed = 0.0
                while elapsed < self.analysis_interval and self.running:
                    time.sleep(1.0)
                    elapsed += 1.0
                    
            except Exception as e:
                self.logger.error(f"Error in analysis loop: {e}")
                time.sleep(5.0)  # Wait before retrying
    
    def analyze_city(self) -> Dict[str, Any]:
        """
        Perform comprehensive city analysis.
        
        Returns:
            Dictionary containing analysis results
        """
        if not self.city.is_valid():
            return {"error": "No valid city loaded"}
        
        try:
            # Basic city information
            city_name = self.city.get_city_name()
            population = self.city.get_city_population()
            money = self.city.get_city_money()
            mayor_mode = self.city.get_mayor_mode()
            
            # Get detailed city stats
            stats = self.city.get_city_stats()
            
            # Calculate derived metrics
            total_population = (stats.residential_population + 
                              stats.commercial_population + 
                              stats.industrial_population)
            
            power_deficit = stats.power_consumed - stats.power_produced
            water_deficit = stats.water_consumed - stats.water_produced
            
            # Store historical data
            self._update_history(population, money)
            
            # Calculate trends
            population_trend = self._calculate_trend(self.population_history)
            money_trend = self._calculate_trend(self.money_history)
            
            analysis = {
                "timestamp": time.time(),
                "city_name": city_name,
                "basic_info": {
                    "population": population,
                    "money": money,
                    "mayor_mode": mayor_mode
                },
                "detailed_stats": {
                    "residential_population": stats.residential_population,
                    "commercial_population": stats.commercial_population,
                    "industrial_population": stats.industrial_population,
                    "total_jobs": stats.total_jobs,
                    "power_produced": stats.power_produced,
                    "power_consumed": stats.power_consumed,
                    "water_produced": stats.water_produced,
                    "water_consumed": stats.water_consumed
                },
                "derived_metrics": {
                    "total_population": total_population,
                    "power_deficit": power_deficit,
                    "water_deficit": water_deficit,
                    "unemployment_rate": self._calculate_unemployment_rate(total_population, stats.total_jobs)
                },
                "trends": {
                    "population": population_trend,
                    "money": money_trend
                },
                "alerts": self._generate_alerts(stats, power_deficit, water_deficit, money)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing city: {e}")
            return {"error": str(e)}
    
    def _update_history(self, population: int, money: int) -> None:
        """Update historical data."""
        self.population_history.append(population)
        self.money_history.append(money)
        
        # Trim history to max size
        if len(self.population_history) > self.max_history_size:
            self.population_history.pop(0)
        if len(self.money_history) > self.max_history_size:
            self.money_history.pop(0)
    
    def _calculate_trend(self, data: list) -> str:
        """Calculate trend from historical data."""
        if len(data) < 2:
            return "insufficient_data"
        
        recent_avg = sum(data[-5:]) / min(5, len(data))
        older_avg = sum(data[:5]) / min(5, len(data))
        
        if recent_avg > older_avg * 1.05:
            return "increasing"
        elif recent_avg < older_avg * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_unemployment_rate(self, population: int, jobs: int) -> float:
        """Calculate unemployment rate."""
        if population == 0:
            return 0.0
        
        # Assume workforce is about 40% of total population
        workforce = population * 0.4
        if workforce == 0:
            return 0.0
        
        unemployed = max(0, workforce - jobs)
        return (unemployed / workforce) * 100.0
    
    def _generate_alerts(self, stats, power_deficit: int, water_deficit: int, money: int) -> list:
        """Generate alerts based on city conditions."""
        alerts = []
        
        # Financial alerts
        if money < 10000:
            alerts.append({
                "type": "financial",
                "severity": "high",
                "message": f"Low treasury: ${money:,}"
            })
        elif money < 50000:
            alerts.append({
                "type": "financial",
                "severity": "medium",
                "message": f"Treasury getting low: ${money:,}"
            })
        
        # Power alerts
        if power_deficit > 0:
            alerts.append({
                "type": "utility",
                "severity": "high",
                "message": f"Power shortage: {power_deficit} MW deficit"
            })
        elif power_deficit > -1000:  # Low surplus
            alerts.append({
                "type": "utility",
                "severity": "low",
                "message": "Low power surplus, consider building more power plants"
            })
        
        # Water alerts
        if water_deficit > 0:
            alerts.append({
                "type": "utility",
                "severity": "high",
                "message": f"Water shortage: {water_deficit} units deficit"
            })
        elif water_deficit > -1000:  # Low surplus
            alerts.append({
                "type": "utility",
                "severity": "low",
                "message": "Low water surplus, consider building more water facilities"
            })
        
        return alerts
    
    def _process_analysis_results(self, results: Dict[str, Any]) -> None:
        """Process and log analysis results."""
        if "error" in results:
            self.logger.error(f"Analysis error: {results['error']}")
            return
        
        city_name = results.get("city_name", "Unknown")
        basic_info = results.get("basic_info", {})
        alerts = results.get("alerts", [])
        
        # Log basic info periodically
        self.logger.info(f"[{city_name}] Pop: {basic_info.get('population', 0):,}, "
                        f"Money: ${basic_info.get('money', 0):,}")
        
        # Log alerts
        for alert in alerts:
            severity = alert.get("severity", "low")
            message = alert.get("message", "Unknown alert")
            
            if severity == "high":
                self.logger.warning(f"ALERT: {message}")
            elif severity == "medium":
                self.logger.info(f"Warning: {message}")
            else:
                self.logger.debug(f"Notice: {message}")
    
    def shutdown(self) -> None:
        """Shutdown the plugin."""
        self.stop_analysis()
        super().shutdown()
    
    def on_city_init(self) -> None:
        """Called when a city is loaded."""
        super().on_city_init()
        
        # Clear historical data for new city
        self.population_history.clear()
        self.money_history.clear()
        
        if self.city.is_valid():
            city_name = self.city.get_city_name()
            self.logger.info(f"Starting analysis for city: {city_name}")
    
    def on_city_shutdown(self) -> None:
        """Called when a city is being shut down."""
        super().on_city_shutdown()
        self.logger.info("City analysis stopped for city shutdown")