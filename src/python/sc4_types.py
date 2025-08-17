"""
SC4 Python Framework - Type Definitions

This module defines strongly-typed Pydantic models for communication between
the C++ framework and Python plugins, providing validation, serialization,
and excellent IDE support.
"""

from pydantic import BaseModel, Field, computed_field
from typing import Optional, Dict, Any
from enum import IntEnum


class MessageType(IntEnum):
    """SC4 Message Type Constants"""
    CITY_INIT = 0x26C63345
    CITY_SHUTDOWN = 0x26C63346
    QUERY_EXEC_START = 0x26ad8e01
    QUERY_EXEC_END = 0x26ad8e02
    CHEAT_ISSUED = 0x230E27AC


class CheatID(IntEnum):
    """Common SC4 Cheat IDs"""
    FUND = 0x6990
    POWER = 0x1DE4F79A
    WATER = 0x1DE4F79B


class SC4Message(BaseModel):
    """
    Represents an SC4 game message.
    
    Provides validation and type safety for messages passed from C++ to Python.
    """
    message_type: int = Field(..., description="The type ID of the message")
    data1: int = Field(default=0, description="First data field (usually uint32)")
    data2: int = Field(default=0, description="Second data field (usually uint32)")
    data3: int = Field(default=0, description="Third data field (usually uint32)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional optional metadata")

    @computed_field
    @property
    def type_name(self) -> str:
        """Get human-readable name for message type"""
        try:
            return MessageType(self.message_type).name
        except ValueError:
            return f"UNKNOWN_0x{self.message_type:08x}"

    def is_city_message(self) -> bool:
        """Check if this is a city-related message"""
        return self.message_type in (MessageType.CITY_INIT, MessageType.CITY_SHUTDOWN)

    def is_cheat_message(self) -> bool:
        """Check if this is a cheat message"""
        return self.message_type == MessageType.CHEAT_ISSUED

    class Config:
        frozen = True  # Make immutable
        use_enum_values = True


class CheatCommand(BaseModel):
    """
    Represents a cheat command issued by the user.
    
    Provides parsing and validation for cheat commands.
    """
    cheat_id: int = Field(..., description="Numeric ID of the cheat")
    text: str = Field(..., description="Text content of the cheat command")
    arguments: Optional[Dict[str, str]] = Field(default=None, description="Parsed arguments if the cheat has parameters")

    @computed_field
    @property
    def id_name(self) -> str:
        """Get human-readable name for cheat ID"""
        try:
            return CheatID(self.cheat_id).name
        except ValueError:
            return f"UNKNOWN_0x{self.cheat_id:08x}"

    def get_argument(self, key: str, default: str = "") -> str:
        """Get a specific argument value"""
        if self.arguments is None:
            return default
        return self.arguments.get(key, default)

    class Config:
        frozen = True


class CityStats(BaseModel):
    """
    City statistics snapshot with validation.
    
    All values represent current state of the city and are validated to be non-negative.
    """
    residential_population: int = Field(default=0, ge=0, description="Residential population count")
    commercial_population: int = Field(default=0, ge=0, description="Commercial population count")
    industrial_population: int = Field(default=0, ge=0, description="Industrial population count")
    total_jobs: int = Field(default=0, ge=0, description="Total available jobs")
    power_produced: int = Field(default=0, ge=0, description="Total power production")
    power_consumed: int = Field(default=0, ge=0, description="Total power consumption")
    water_produced: int = Field(default=0, ge=0, description="Total water production")
    water_consumed: int = Field(default=0, ge=0, description="Total water consumption")
    
    @computed_field
    @property
    def total_population(self) -> int:
        """Calculate total city population"""
        return self.residential_population + self.commercial_population + self.industrial_population

    @computed_field
    @property
    def power_surplus(self) -> int:
        """Calculate power surplus/deficit (negative means deficit)"""
        return self.power_produced - self.power_consumed

    @computed_field
    @property
    def water_surplus(self) -> int:
        """Calculate water surplus/deficit (negative means deficit)"""
        return self.water_produced - self.water_consumed


class CityInfo(BaseModel):
    """
    Basic city information with validation.
    """
    name: str = Field(default="", description="City name")
    population: int = Field(default=0, ge=0, description="Total city population")
    money: int = Field(default=0, description="City treasury (can be negative)")
    mayor_mode: bool = Field(default=False, description="Whether mayor mode is active")
    city_date: int = Field(default=0, ge=0, description="Game date")
    city_time: int = Field(default=0, ge=0, description="Game time")
    is_valid: bool = Field(default=False, description="Whether the city data is valid")

    def model_post_init(self, __context) -> None:
        """Validate city info after creation"""
        if not self.is_valid:
            # Reset all values if city is invalid
            object.__setattr__(self, 'name', "")
            object.__setattr__(self, 'population', 0)
            object.__setattr__(self, 'money', 0)
            object.__setattr__(self, 'mayor_mode', False)
            object.__setattr__(self, 'city_date', 0)
            object.__setattr__(self, 'city_time', 0)

    class Config:
        frozen = True


class PluginResponse(BaseModel):
    """
    Standard response format for plugin operations.
    """
    success: bool = Field(..., description="Whether the operation succeeded")
    message: Optional[str] = Field(default=None, description="Optional status or error message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Optional response data")

    @classmethod
    def success_response(cls, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> "PluginResponse":
        """Create a success response"""
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, message: str, data: Optional[Dict[str, Any]] = None) -> "PluginResponse":
        """Create an error response"""
        return cls(success=False, message=message, data=data)

    class Config:
        frozen = True