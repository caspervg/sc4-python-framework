"""
Basic Cheats Plugin for SC4 Python Framework

This plugin demonstrates how to create basic cheats for SimCity 4 using the Python framework.
"""

from sc4_plugin_base import CheatPlugin
from sc4_types import CheatCommand
from typing import Dict

class BasicCheatsPlugin(CheatPlugin):
    """
    Plugin that provides basic cheats for SimCity 4.
    """
    
    def get_plugin_info(self) -> Dict[str, str]:
        return {
            "name": "Basic Cheats",
            "version": "1.0.0",
            "description": "Provides basic cheats like money",
            "author": "SC4 Python Framework"
        }
    
    def initialize(self) -> bool:
        """Initialize the plugin and register cheats."""
        if not super().initialize():
            return False
        
        # Register our cheats
        self.register_cheat("swimminginit", "Set treasure to a high amount",)
        
        cheats = self.get_registered_cheats()
        self.logger.info(f"Registered {len(cheats)} cheats")
        return True
    
    def process_cheat(self, cheat: CheatCommand) -> bool:
        """Process a cheat command that this plugin handles."""
        cheat_text = cheat.text.lower()
        
        if cheat_text == "swimminginit":
            self.max_money()
            return True
        
        return False
    
    def add_money(self) -> None:
        """Add 1,000,000 simoleons to the city treasury."""
        city_info = self.get_city_info()
        if not city_info or not city_info.is_valid:
            self.logger.warning("No city loaded")
            return
        
        amount = 1_000_000
        # Note: actual money manipulation would need C++ wrapper implementation
        self.logger.info(f"Would add ${amount:,} to treasury (not yet implemented)")
        self.logger.info(f"Current balance: ${city_info.money:,}")
    
    def max_money(self) -> None:
        """Set city money to maximum amount."""
        city_info = self.get_city_info()
        if not city_info or not city_info.is_valid:
            self.logger.warning("No city loaded")
            return
        
        amount = 999_999_999
        self.logger.info(f"Would set treasury to: ${amount:,} (not yet implemented)")
        self.logger.info(f"Current balance: ${city_info.money:,}")
    
    def on_city_init(self) -> None:
        """Called when a city is loaded."""
        city_info = self.get_city_info()
        if city_info and city_info.is_valid:
            self.logger.info(f"Basic cheats available for city: {city_info.name}")
    
    def on_city_shutdown(self) -> None:
        """Called when a city is being shut down."""
        self.logger.info("Basic cheats disabled for city shutdown")


# Plugin instance - this is what gets loaded by the framework
plugin_instance = BasicCheatsPlugin