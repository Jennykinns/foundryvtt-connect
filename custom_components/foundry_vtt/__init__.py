"""The Foundry VTT integration."""
from __future__ import annotations

import logging
import json
from typing import Any

from homeassistant.components import webhook
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_WEBHOOK_ID

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Foundry VTT component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Foundry VTT from a config entry."""
    webhook_id = entry.data[CONF_WEBHOOK_ID]
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "webhook_id": webhook_id,
        "data": {},
    }
    
    webhook.async_register(
        hass, DOMAIN, "Foundry VTT Webhook", webhook_id, handle_webhook
    )
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        webhook_id = entry.data[CONF_WEBHOOK_ID]
        webhook.async_unregister(hass, webhook_id)
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def handle_webhook(hass: HomeAssistant, webhook_id: str, request) -> None:
    """Handle webhook callback."""
    try:
        data = await request.json()
        _LOGGER.debug("Received Foundry VTT data: %s", data)
        
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if entry_data["webhook_id"] == webhook_id:
                # Store the entire data set
                hass.data[DOMAIN][entry_id]["data"] = data
                
                # Extract endpoint and message details
                endpoint = data.get("endpoint", "unknown")
                message_data = data.get("data", {})
                
                # Fire an event that automations can react to
                event_data = {
                    "endpoint": endpoint,
                    "data": message_data,
                }
                
                hass.bus.async_fire(f"{DOMAIN}_event", event_data)
                
                # Update sensors
                for entity_id in hass.states.async_entity_ids("sensor"):
                    if entity_id.startswith(f"sensor.{DOMAIN}_"):
                        hass.async_create_task(
                            hass.services.async_call(
                                "homeassistant", "update_entity", {"entity_id": entity_id}
                            )
                        )
                
                break
                
    except Exception as ex:
        _LOGGER.error("Error processing Foundry VTT webhook: %s", ex)