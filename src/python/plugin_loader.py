"""
Plugin Loader for SC4 Python Framework

This module handles the loading and management of Python plugins for SimCity 4.
"""

import os
import sys
import importlib.util
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from sc4_plugin_base import SC4PluginBase

class PluginLoader:
    """
    Handles loading and managing SC4 Python plugins.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.loaded_modules = {}
        
        # Set up logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Set up Python logging to integrate with the C++ logging system."""
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def load_plugin(self, filepath: str, city_wrapper) -> Optional[SC4PluginBase]:
        """
        Load a plugin from a Python file.
        
        Args:
            filepath: Path to the Python plugin file
            city_wrapper: CityWrapper instance to pass to the plugin
            
        Returns:
            Loaded plugin instance or None if loading failed
        """
        try:
            # Convert to Path object for easier manipulation
            plugin_path = Path(filepath)
            
            if not plugin_path.exists():
                self.logger.error(f"Plugin file does not exist: {filepath}")
                return None
            
            if not plugin_path.suffix == '.py':
                self.logger.error(f"Plugin file must be a Python file: {filepath}")
                return None
            
            # Get module name from filename
            module_name = plugin_path.stem
            
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec is None or spec.loader is None:
                self.logger.error(f"Could not create module spec for: {filepath}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            
            # Add to sys.modules before execution
            sys.modules[module_name] = module
            self.loaded_modules[module_name] = module
            
            # Execute the module
            spec.loader.exec_module(module)
            
            # Find the plugin class
            plugin_class = self._find_plugin_class(module)
            if plugin_class is None:
                self.logger.error(f"No plugin class found in: {filepath}")
                return None
            
            # Instantiate the plugin
            plugin_instance = plugin_class(city_wrapper)
            
            if not isinstance(plugin_instance, SC4PluginBase):
                self.logger.error(f"Plugin class must inherit from SC4PluginBase: {filepath}")
                return None
            
            self.logger.info(f"Successfully loaded plugin: {plugin_instance.name} v{plugin_instance.version}")
            return plugin_instance
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {filepath}: {e}")
            return None
    
    def _find_plugin_class(self, module) -> Optional[type]:
        """
        Find the main plugin class in a module.
        
        Args:
            module: Python module to search
            
        Returns:
            Plugin class or None if not found
        """
        # Look for classes that inherit from SC4PluginBase
        for name in dir(module):
            obj = getattr(module, name)
            
            # Check if it's a class and inherits from SC4PluginBase
            if (isinstance(obj, type) and 
                issubclass(obj, SC4PluginBase) and 
                obj is not SC4PluginBase):
                
                # Prefer classes with "Plugin" in the name
                if "Plugin" in name:
                    return obj
        
        # If no class with "Plugin" in name, return first SC4PluginBase subclass
        for name in dir(module):
            obj = getattr(module, name)
            if (isinstance(obj, type) and 
                issubclass(obj, SC4PluginBase) and 
                obj is not SC4PluginBase):
                return obj
        
        return None
    
    def unload_plugin(self, module_name: str) -> bool:
        """
        Unload a plugin module.
        
        Args:
            module_name: Name of the module to unload
            
        Returns:
            True if unloaded successfully
        """
        try:
            if module_name in self.loaded_modules:
                # Remove from our tracking
                del self.loaded_modules[module_name]
                
                # Remove from sys.modules if present
                if module_name in sys.modules:
                    del sys.modules[module_name]
                
                self.logger.info(f"Unloaded plugin module: {module_name}")
                return True
            else:
                self.logger.warning(f"Module not found for unloading: {module_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to unload plugin module {module_name}: {e}")
            return False
    
    def reload_plugin(self, filepath: str, city_wrapper) -> Optional[SC4PluginBase]:
        """
        Reload a plugin from file.
        
        Args:
            filepath: Path to the plugin file
            city_wrapper: CityWrapper instance
            
        Returns:
            Reloaded plugin instance or None if failed
        """
        module_name = Path(filepath).stem
        
        # Unload existing module if present
        self.unload_plugin(module_name)
        
        # Load the plugin again
        return self.load_plugin(filepath, city_wrapper)
    
    def validate_plugin(self, plugin_instance: SC4PluginBase) -> bool:
        """
        Validate that a plugin meets the requirements.
        
        Args:
            plugin_instance: Plugin to validate
            
        Returns:
            True if plugin is valid
        """
        try:
            # Check required properties
            if not hasattr(plugin_instance, 'name') or not plugin_instance.name:
                self.logger.error("Plugin missing required 'name' property")
                return False
            
            if not hasattr(plugin_instance, 'version') or not plugin_instance.version:
                self.logger.error("Plugin missing required 'version' property")
                return False
            
            if not hasattr(plugin_instance, 'description') or not plugin_instance.description:
                self.logger.error("Plugin missing required 'description' property")
                return False
            
            # Check required methods
            required_methods = ['initialize', 'shutdown', 'handle_message']
            for method in required_methods:
                if not hasattr(plugin_instance, method) or not callable(getattr(plugin_instance, method)):
                    self.logger.error(f"Plugin missing required method: {method}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating plugin: {e}")
            return False
    
    def get_loaded_modules(self) -> Dict[str, Any]:
        """
        Get dictionary of loaded plugin modules.
        
        Returns:
            Dictionary mapping module names to modules
        """
        return self.loaded_modules.copy()
    
    def discover_plugins(self, directory: str) -> List[str]:
        """
        Discover plugin files in a directory.
        
        Args:
            directory: Directory to search for plugins
            
        Returns:
            List of plugin file paths
        """
        plugin_files = []
        
        try:
            plugin_dir = Path(directory)
            if not plugin_dir.exists():
                self.logger.warning(f"Plugin directory does not exist: {directory}")
                return plugin_files
            
            # Find all .py files that don't start with underscore
            for file_path in plugin_dir.glob("*.py"):
                if not file_path.name.startswith('_'):
                    plugin_files.append(str(file_path))
            
            self.logger.info(f"Discovered {len(plugin_files)} plugin files in {directory}")
            
        except Exception as e:
            self.logger.error(f"Error discovering plugins in {directory}: {e}")
        
        return plugin_files