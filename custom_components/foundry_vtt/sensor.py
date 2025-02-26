"""Platform for sensor integration."""
from __future__ import annotations

import logging
from typing import Any, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ACTOR_HP, ACTOR_AC, COMBAT_STATUS, COMBAT_TURN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Foundry VTT sensor platform."""
    # Create sensors
    sensors = [
        FoundryVTTCurrentHPSensor(hass, entry),
        FoundryVTTMaxHPSensor(hass, entry),
        FoundryVTTACSensor(hass, entry),
        FoundryVTTCombatStatusSensor(hass, entry),
        FoundryVTTCombatTurnSensor(hass, entry),
    ]
    
    async_add_entities(sensors)


class FoundryVTTSensor(SensorEntity):
    """Representation of a Foundry VTT Sensor."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self.entry = entry
        self.entry_id = entry.entry_id
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="Foundry VTT",
            name="Foundry Virtual Tabletop",
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.entry_id in self.hass.data[DOMAIN]

    def _get_data(self) -> Any:
        """Get current data from the entity."""
        return self.hass.data[DOMAIN][self.entry_id]["data"]


class FoundryVTTCurrentHPSensor(FoundryVTTSensor):
    """Sensor for current HP."""

    _attr_name = "Current HP"
    _attr_icon = "mdi:heart"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "HP"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.entry_id}_current_hp"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        data = self._get_data()
        if not data:
            return 0
            
        try:
            if "data" in data and "hp" in data["data"]:
                return data["data"]["hp"]["value"]
            
            # For actor-specific data
            if "endpoint" in data and data["endpoint"].startswith("actor/") and "data" in data:
                actor_data = data["data"]
                if "hp" in actor_data and "value" in actor_data["hp"]:
                    return actor_data["hp"]["value"]
        except Exception as e:
            _LOGGER.error("Error extracting current HP: %s", e)
            
        return 0


class FoundryVTTMaxHPSensor(FoundryVTTSensor):
    """Sensor for max HP."""

    _attr_name = "Max HP"
    _attr_icon = "mdi:heart-outline"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "HP"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.entry_id}_max_hp"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        data = self._get_data()
        if not data:
            return 0
            
        try:
            if "data" in data and "hp" in data["data"]:
                return data["data"]["hp"]["max"]
            
            # For actor-specific data
            if "endpoint" in data and data["endpoint"].startswith("actor/") and "data" in data:
                actor_data = data["data"]
                if "hp" in actor_data and "max" in actor_data["hp"]:
                    return actor_data["hp"]["max"]
        except Exception as e:
            _LOGGER.error("Error extracting max HP: %s", e)
            
        return 0


class FoundryVTTACSensor(FoundryVTTSensor):
    """Sensor for AC."""

    _attr_name = "Armor Class"
    _attr_icon = "mdi:shield"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.entry_id}_ac"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        data = self._get_data()
        if not data:
            return 0
            
        try:
            if "data" in data and "ac" in data["data"]:
                return data["data"]["ac"]
            
            # For actor-specific data
            if "endpoint" in data and data["endpoint"].startswith("actor/") and "data" in data:
                actor_data = data["data"]
                if "ac" in actor_data:
                    return actor_data["ac"]
        except Exception as e:
            _LOGGER.error("Error extracting AC: %s", e)
            
        return 0


class FoundryVTTCombatStatusSensor(FoundryVTTSensor):
    """Sensor for combat status."""

    _attr_name = "Combat Status"
    _attr_icon = "mdi:sword-cross"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.entry_id}_combat_status"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        data = self._get_data()
        if not data:
            return "No Combat"
            
        try:
            if "endpoint" in data and data["endpoint"] == "combat/event" and "data" in data:
                event_data = data["data"]
                if "event" in event_data:
                    if event_data["event"] == "combat_start":
                        return "In Combat"
                    elif event_data["event"] == "combat_end":
                        return "No Combat"
                    elif event_data["event"] == "combat_round":
                        return f"Round {event_data.get('round', '?')}"
        except Exception as e:
            _LOGGER.error("Error extracting combat status: %s", e)
            
        return "Unknown"


class FoundryVTTCombatTurnSensor(FoundryVTTSensor):
    """Sensor for current turn in combat."""

    _attr_name = "Current Turn"
    _attr_icon = "mdi:account-clock"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.entry_id}_combat_turn"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        data = self._get_data()
        if not data:
            return "No active turn"
            
        try:
            if "endpoint" in data and data["endpoint"] == "combat/event" and "data" in data:
                event_data = data["data"]
                if "event" in event_data and event_data["event"] == "combat_turn" and "current" in event_data:
                    current = event_data["current"]
                    return f"{current.get('name', 'Unknown')} (Initiative: {current.get('initiative', '?')})"
        except Exception as e:
            _LOGGER.error("Error extracting combat turn: %s", e)
            
        return "No active turn"