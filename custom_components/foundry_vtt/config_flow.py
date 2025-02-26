"""Config flow for Foundry VTT integration."""
from __future__ import annotations

import logging
import uuid
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import selector

from .const import DOMAIN, CONF_WEBHOOK_ID

_LOGGER = logging.getLogger(__name__)

class FoundryVTTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Foundry VTT."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            webhook_id = str(uuid.uuid4())
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_WEBHOOK_ID, default=webhook_id): str,
                    }
                ),
                description_placeholders={
                    "webhook_url": f"https://YOURHOMEASSISTANTDOMAIN/api/webhook/{webhook_id}",
                },
            )

        await self.async_set_unique_id(user_input[CONF_WEBHOOK_ID])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title="Foundry VTT",
            data=user_input,
        )