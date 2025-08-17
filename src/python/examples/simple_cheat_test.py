"""
Simple test plugin to verify cheat registration works correctly.
"""

from sc4_plugin_base import CheatPlugin
from sc4_types import CheatCommand
from typing import Dict


class SimpleCheatTestPlugin(CheatPlugin):
    """
    Simple test plugin to verify the cheat registration pipeline.
    """
    
    def get_plugin_info(self) -> Dict[str, str]:
        return {
            "name": "Simple Cheat Test Plugin",
            "version": "1.0.0", 
            "description": "Tests basic cheat registration",
            "author": "SC4 Python Framework"
        }
    
    def initialize(self) -> bool:
        """Initialize the plugin and register a simple cheat."""
        print("SimpleCheatTest: Initializing...")
        
        # Register a simple test cheat
        self.register_cheat("testcheat", "Simple test cheat that just logs a message")
        
        print("SimpleCheatTest: Registered 'testcheat' command")
        self.logger.info("SimpleCheatTestPlugin initialized successfully")
        return super().initialize()
    
    def process_cheat(self, cheat: CheatCommand) -> bool:
        """Process our registered cheats."""
        if cheat.text.lower() == "testcheat":
            print("=== TEST CHEAT EXECUTED ===")
            self.logger.info("testcheat command executed successfully!")
            print("If you can see this, the cheat registration pipeline is working!")
            return True
        
        return False


# Plugin instance - this is what gets loaded by the framework
plugin_instance = SimpleCheatTestPlugin