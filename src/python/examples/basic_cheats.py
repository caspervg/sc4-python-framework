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
            self.set_treasure_max()
            return True
        
        return False
    
    def add_money(self) -> None:
        """Add 1,000,000 simoleons to the city treasury."""
        if not self.city_wrapper or not self.city_wrapper.is_valid():
            self.logger.warning("No city loaded")
            return
        
        amount = 1_000_000
        if self.city_wrapper.add_city_money(amount):
            self.logger.info(f"Added ${amount:,} to treasury")
            self.logger.info(f"New balance: ${self.city_wrapper.get_city_money():,}")
        else:
            self.logger.error("Failed to add city money")
    
    def set_treasure_max(self) -> None:
        """Set city money to maximum amount (999,999,999)."""
        if not self.city_wrapper or not self.city_wrapper.is_valid():
            self.logger.warning("No city loaded")
            return
        
        amount = 999_999_999
        if self.city_wrapper.set_city_money(amount):
            self.logger.info(f"Set treasury to: ${amount:,}")
            self.logger.info(f"New balance: ${self.city_wrapper.get_city_money():,}")
        else:
            self.logger.error("Failed to set city money")
    
    def on_city_init(self) -> bool:
        """Called when a city is loaded."""
        if self.city_wrapper and self.city_wrapper.is_valid():
            city_name = self.city_wrapper.get_city_name()
            self.logger.info(f"Basic cheats available for city: {city_name}")
        return True
    
    def on_city_shutdown(self) -> bool:
        """Called when a city is being shut down."""
        self.logger.info("Basic cheats disabled for city shutdown")
        return True


# Plugin instance - this is what gets loaded by the framework
plugin_instance = BasicCheatsPlugin