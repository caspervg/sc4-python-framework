"""
SC4 Python Framework - Base Plugin Classes

This module provides base classes for creating SC4 Python plugins with
strong typing and proper integration with the framework.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from sc4_types import CheatCommand, SC4Message, CityInfo, CityStats, PluginResponse, MessageType
from sc4_logger import get_logger


class SC4PluginBase(ABC):
    """
    Base class for all SC4 Python plugins.
    
    Provides the basic interface that all plugins must implement,
    with strong typing and validation through Pydantic models.
    """
    
    def __init__(self, city_wrapper=None):
        """
        Initialize the plugin.
        
        Args:
            city_wrapper: The C++ CityWrapper object for interacting with the game
        """
        self.city_wrapper = city_wrapper
        self.plugin_name = self.__class__.__name__
        self._initialized = False
        self.logger = get_logger(self.plugin_name)

    @abstractmethod
    def get_plugin_info(self) -> Dict[str, str]:
        """
        Get plugin information.
        
        Returns:
            Dictionary containing plugin metadata (name, version, description, author)
        """
        pass

    def initialize(self) -> bool:
        """
        Initialize the plugin. Called when the plugin is loaded.
        
        Returns:
            True if initialization succeeded, False otherwise
        """
        self._initialized = True
        return True

    def shutdown(self) -> None:
        """
        Shutdown the plugin. Called when the plugin is unloaded.
        """
        self._initialized = False

    def handle_message(self, message: SC4Message) -> bool:
        """
        Handle an SC4 game message.
        
        Args:
            message: The SC4Message object containing message data
            
        Returns:
            True if the message was handled, False otherwise
        """
        if message.is_city_message():
            if message.message_type == MessageType.CITY_INIT:
                return self.on_city_init()
            elif message.message_type == MessageType.CITY_SHUTDOWN:
                return self.on_city_shutdown()
        
        return False

    def handle_cheat(self, cheat: CheatCommand) -> bool:
        """
        Handle a cheat command.
        
        Args:
            cheat: The CheatCommand object containing cheat data
            
        Returns:
            True if the cheat was handled, False otherwise
        """
        return False

    def on_city_init(self) -> bool:
        """
        Called when a city is loaded.
        
        Returns:
            True if handled successfully
        """
        return True

    def on_city_shutdown(self) -> bool:
        """
        Called when a city is unloaded.
        
        Returns:
            True if handled successfully
        """
        return True

    def get_city_info(self) -> Optional[CityInfo]:
        """
        Get current city information.
        
        Returns:
            CityInfo object if city is valid, None otherwise
        """
        if not self.city_wrapper or not self.city_wrapper.is_valid():
            return None
            
        return CityInfo(
            name=self.city_wrapper.get_city_name(),
            population=self.city_wrapper.get_city_population(),
            money=self.city_wrapper.get_city_money(),
            mayor_mode=self.city_wrapper.get_mayor_mode(),
            city_date=self.city_wrapper.get_city_date(),
            city_time=self.city_wrapper.get_city_time(),
            is_valid=True
        )

    def get_city_stats(self) -> Optional[CityStats]:
        """
        Get current city statistics.
        
        Returns:
            CityStats object if city is valid, None otherwise
        """
        if not self.city_wrapper or not self.city_wrapper.is_valid():
            return None
            
        stats = self.city_wrapper.get_city_stats()
        return CityStats(
            residential_population=stats.residential_population,
            commercial_population=stats.commercial_population,
            industrial_population=stats.industrial_population,
            total_jobs=stats.total_jobs,
            power_produced=stats.power_produced,
            power_consumed=stats.power_consumed,
            water_produced=stats.water_produced,
            water_consumed=stats.water_consumed
        )


class CheatPlugin(SC4PluginBase):
    """
    Specialized base class for plugins that primarily handle cheat commands.
    """
    
    def __init__(self, city_wrapper=None):
        super().__init__(city_wrapper)
        self._registered_cheats: Dict[str, str] = {}

    def register_cheat(self, cheat_text: str, description: str) -> None:
        """
        Register a cheat command that this plugin handles.
        
        Args:
            cheat_text: The cheat text (e.g., "myplugin:givemoney")
            description: Human-readable description of what the cheat does
        """
        # Always store cheats in lowercase for consistent case-insensitive handling
        self._registered_cheats[cheat_text.lower()] = description

    def get_registered_cheats(self) -> Dict[str, str]:
        """
        Get all cheats registered by this plugin.
        
        Returns:
            Dictionary mapping cheat text to descriptions
        """
        return self._registered_cheats.copy()

    def handle_cheat(self, cheat: CheatCommand) -> bool:
        """
        Handle a cheat command. Subclasses should override this.
        
        Args:
            cheat: The CheatCommand object
            
        Returns:
            True if the cheat was handled, False otherwise
        """
        cheat_text = cheat.text.lower()
        if cheat_text in self._registered_cheats:
            return self.process_cheat(cheat)
        return False

    @abstractmethod
    def process_cheat(self, cheat: CheatCommand) -> bool:
        """
        Process a cheat command that this plugin handles.
        
        Args:
            cheat: The CheatCommand object
            
        Returns:
            True if processing succeeded, False otherwise
        """
        pass


class SC4MessagePlugin(SC4PluginBase, ABC):
    """
    Specialized base class for plugins that primarily handle game messages.
    """
    
    def __init__(self, city_wrapper=None):
        super().__init__(city_wrapper)
        self._message_handlers: Dict[int, str] = {}

    def register_message_handler(self, message_type: int, handler_method: str) -> None:
        """
        Register a handler method for a specific message type.
        
        Args:
            message_type: The message type ID to handle
            handler_method: Name of the method to call for this message type
        """
        self._message_handlers[message_type] = handler_method

    def handle_message(self, message: SC4Message) -> bool:
        """
        Handle an SC4 game message using registered handlers.
        
        Args:
            message: The SC4Message object
            
        Returns:
            True if the message was handled, False otherwise
        """
        # First call parent handler for standard messages
        if super().handle_message(message):
            return True
            
        # Then check for custom registered handlers
        if message.message_type in self._message_handlers:
            handler_name = self._message_handlers[message.message_type]
            if hasattr(self, handler_name):
                handler = getattr(self, handler_name)
                return handler(message)
                
        return False