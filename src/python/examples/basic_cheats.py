"""
Basic Cheats Plugin for SC4 Python Framework

This plugin demonstrates how to create basic cheats for SimCity 4 using the Python framework.
"""

from sc4_plugin_base import CheatPlugin
import logging

class BasicCheatsPlugin(CheatPlugin):
    """
    Plugin that provides basic cheats for SimCity 4.
    """
    
    @property
    def name(self) -> str:
        return "Basic Cheats"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Provides basic cheats like money, mayor mode, and utilities"
    
    @property
    def author(self) -> str:
        return "SC4 Python Framework"
    
    def initialize(self) -> bool:
        """Initialize the plugin and register cheats."""
        if not super().initialize():
            return False
        
        # Register our cheats
        self.register_cheat("moolah", self.add_money, "Add 1,000,000 to city treasury")
        self.register_cheat("weaknesspays", self.add_money, "Add 1,000,000 to city treasury")
        self.register_cheat("payola", self.max_money, "Set money to maximum amount")
        self.register_cheat("mayormode", self.toggle_mayor_mode, "Toggle mayor mode on/off")
        self.register_cheat("power", self.toggle_free_power, "Toggle free power")
        self.register_cheat("water", self.toggle_free_water, "Toggle free water")
        self.register_cheat("powerplease", self.add_power, "Add power to city")
        self.register_cheat("waterplease", self.add_water, "Add water to city")
        
        self.logger.info(f"Registered {len(self.cheats)} cheats")
        return True
    
    def add_money(self) -> None:
        """Add 1,000,000 simoleons to the city treasury."""
        if not self.city.is_valid():
            self.logger.warning("No city loaded")
            return
        
        amount = 1_000_000
        if self.city.add_city_money(amount):
            current_money = self.city.get_city_money()
            self.logger.info(f"Added ${amount:,} to treasury. Current balance: ${current_money:,}")
        else:
            self.logger.error("Failed to add money to treasury")
    
    def max_money(self) -> None:
        """Set city money to maximum amount."""
        if not self.city.is_valid():
            self.logger.warning("No city loaded")
            return
        
        max_amount = 999_999_999  # SC4 maximum
        if self.city.set_city_money(max_amount):
            self.logger.info(f"Set treasury to maximum: ${max_amount:,}")
        else:
            self.logger.error("Failed to set maximum money")
    
    def toggle_mayor_mode(self) -> None:
        """Toggle mayor mode on/off."""
        if not self.city.is_valid():
            self.logger.warning("No city loaded")
            return
        
        current_mode = self.city.get_mayor_mode()
        new_mode = not current_mode
        
        if self.city.set_mayor_mode(new_mode):
            mode_str = "ON" if new_mode else "OFF"
            self.logger.info(f"Mayor mode: {mode_str}")
        else:
            self.logger.error("Failed to toggle mayor mode")
    
    def toggle_free_power(self) -> None:
        """Toggle free power for the city."""
        if not self.city.is_valid():
            self.logger.warning("No city loaded")
            return
        
        # This would need integration with power simulator
        # For now, just log the action
        self.logger.info("Free power toggle requested (not yet implemented)")
    
    def toggle_free_water(self) -> None:
        """Toggle free water for the city."""
        if not self.city.is_valid():
            self.logger.warning("No city loaded")
            return
        
        # This would need integration with water simulator
        # For now, just log the action
        self.logger.info("Free water toggle requested (not yet implemented)")
    
    def add_power(self) -> None:
        """Add power to the city."""
        if not self.city.is_valid():
            self.logger.warning("No city loaded")
            return
        
        # This would need integration with power simulator
        # For now, just log the action
        self.logger.info("Add power requested (not yet implemented)")
    
    def add_water(self) -> None:
        """Add water to the city."""
        if not self.city.is_valid():
            self.logger.warning("No city loaded")
            return
        
        # This would need integration with water simulator
        # For now, just log the action
        self.logger.info("Add water requested (not yet implemented)")
    
    def handle_message(self, message) -> bool:
        """Handle SC4 messages, particularly cheat messages."""
        if not self.enabled:
            return False
        
        # Let the parent class handle cheat message routing
        return super().handle_message(message)
    
    def on_city_init(self) -> None:
        """Called when a city is loaded."""
        if self.city.is_valid():
            city_name = self.city.get_city_name()
            self.logger.info(f"Basic cheats available for city: {city_name}")
    
    def on_city_shutdown(self) -> None:
        """Called when a city is being shut down."""
        self.logger.info("Basic cheats disabled for city shutdown")