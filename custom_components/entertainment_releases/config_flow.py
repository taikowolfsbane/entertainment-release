from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult

from .const import CONF_API_TOKEN, CONF_REGION, DEFAULT_REGION, DOMAIN
from .coordinator import test_tmdb_connection


class EntertainmentReleasesConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):
    """Handle configuration for Entertainment Releases."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await test_tmdb_connection(
                    self.hass, user_input[CONF_API_TOKEN]
                )
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="Entertainment Releases",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_TOKEN): str,
                    vol.Optional(
                        CONF_REGION, default=DEFAULT_REGION
                    ): str,
                }
            ),
            errors=errors,
        )
