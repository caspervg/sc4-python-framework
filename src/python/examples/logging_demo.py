"""
Example plugin demonstrating integrated logging with C++ logger.

This plugin shows how Python print() statements and logging calls
are automatically captured and sent to the C++ logging system.
"""

from sc4_plugin_base import CheatPlugin
from sc4_types import CheatCommand
from typing import Dict


class LoggingDemoPlugin(CheatPlugin):
    """
    Demo plugin that shows various logging methods.
    """
    
    def get_plugin_info(self) -> Dict[str, str]:
        return {
            "name": "Logging Demo Plugin",
            "version": "1.0.0", 
            "description": "Demonstrates integrated Python/C++ logging",
            "author": "SC4 Python Framework"
        }
    
    def initialize(self) -> bool:
        """Initialize the plugin and register cheats."""
        # These will all appear in the C++ log file
        print("LoggingDemo: This is a print() statement!")
        
        self.logger.info("This is a Python logger.info() call")
        self.logger.warning("This is a Python logger.warning() call")
        self.logger.error("This is a Python logger.error() call")
        # Register our demo cheats
        self.register_cheat("logtest", "Test various logging methods")
        self.register_cheat("loglevels", "Demonstrate different log levels")
        
        self.logger.info("LoggingDemoPlugin initialized successfully")
        return super().initialize()
    
    def process_cheat(self, cheat: CheatCommand) -> bool:
        """Process our registered cheats."""
        if cheat.text.lower() == "logtest":
            self._test_logging_methods()
            return True
        elif cheat.text.lower() == "loglevels":
            self._test_log_levels()
            return True
        
        return False
    
    def _test_logging_methods(self) -> None:
        """Test different ways of logging from Python."""
        print("=== Testing Different Logging Methods ===")
        
        # Standard print (captured by our custom stdout)
        print(f"Print: Plugin {self.plugin_name} is testing logging")
        
        # Python logger (forwarded to C++ logger)
        self.logger.info("Logger: This goes through Python's logging system")
        
        # Direct C++ logging (if available)
        try:
            import sc4_native
            sc4_native.log_info("Direct: This calls C++ logging directly")
        except (ImportError, AttributeError):
            print("Direct C++ logging not available")
        
        # Multi-line logging
        multi_line = """This is a multi-line
        log message that spans
        several lines"""
        self.logger.info(f"Multi-line message: {multi_line}")
        
        print("=== Logging Methods Test Complete ===")
    
    def _test_log_levels(self) -> None:
        """Test different log levels."""
        print("=== Testing Log Levels ===")
        
        self.logger.debug("This is a DEBUG level message")
        self.logger.info("This is an INFO level message") 
        self.logger.warning("This is a WARNING level message")
        self.logger.error("This is an ERROR level message")
        self.logger.critical("This is a CRITICAL level message")
        
        # Test with city information if available
        city_info = self.get_city_info()
        if city_info and city_info.is_valid:
            self.logger.info(f"Current city: {city_info.name} (Population: {city_info.population:,})")
            self.logger.info(f"City money: ${city_info.money:,}")
        else:
            self.logger.warning("No valid city loaded")
        
        print("=== Log Levels Test Complete ===")
    
    def on_city_init(self) -> bool:
        """Called when a city is loaded."""
        city_info = self.get_city_info()
        if city_info:
            print(f"City loaded: {city_info.name}")
            self.logger.info(f"City '{city_info.name}' initialized with population {city_info.population:,}")
        
        return super().on_city_init()
    
    def on_city_shutdown(self) -> bool:
        """Called when a city is unloaded."""
        print("City is shutting down")
        self.logger.info("City shutdown event received")
        
        return super().on_city_shutdown()


# Plugin instance - this is what gets loaded by the framework
plugin_instance = LoggingDemoPlugin