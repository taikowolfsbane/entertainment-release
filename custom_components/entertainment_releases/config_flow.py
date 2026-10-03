from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import (
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_API_TOKEN,
    CONF_DIGITAL_DAYS,
    CONF_REFRESH_INTERVAL,
    CONF_REGION,
    CONF_THEATRICAL_DAYS,
    CONF_TV_DAYS,
    DEFAULT_DIGITAL_DAYS,
    DEFAULT_REFRESH_INTERVAL,
    DEFAULT_REGION,
    DEFAULT_THEATRICAL_DAYS,
    DEFAULT_TV_DAYS,
    DOMAIN,
    MAX_LOOKAHEAD_DAYS,
    MAX_REFRESH_INTERVAL,
    MIN_LOOKAHEAD_DAYS,
    MIN_REFRESH_INTERVAL,
)
from .coordinator import test_tmdb_connection


def _number_selector(minimum: int, maximum: int) -> selector.NumberSelector:
    """Create a whole-number box selector."""
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=minimum,
            max=maximum,
            step=1,
            mode=selector.NumberSelectorMode.BOX,
        )
    )


class EntertainmentReleasesConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle configuration for Entertainment Releases."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle initial setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await test_tmdb_connection(
                    self.hass,
                    user_input[CONF_API_TOKEN],
                )
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="Entertainment Releases",
                    data=user_input,
                    options={
                        CONF_THEATRICAL_DAYS: DEFAULT_THEATRICAL_DAYS,
                        CONF_DIGITAL_DAYS: DEFAULT_DIGITAL_DAYS,
                        CONF_TV_DAYS: DEFAULT_TV_DAYS,
                        CONF_REFRESH_INTERVAL: DEFAULT_REFRESH_INTERVAL,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_TOKEN): str,
                    vol.Optional(
                        CONF_REGION,
                        default=DEFAULT_REGION,
                    ): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> EntertainmentReleasesOptionsFlow:
        """Create the options flow."""
        return EntertainmentReleasesOptionsFlow()


class EntertainmentReleasesOptionsFlow(OptionsFlowWithReload):
    """Manage Entertainment Releases options."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage integration options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_THEATRICAL_DAYS: int(user_input[CONF_THEATRICAL_DAYS]),
                    CONF_DIGITAL_DAYS: int(user_input[CONF_DIGITAL_DAYS]),
                    CONF_TV_DAYS: int(user_input[CONF_TV_DAYS]),
                    CONF_REFRESH_INTERVAL: int(
                        user_input[CONF_REFRESH_INTERVAL]
                    ),
                },
            )

        options = self.config_entry.options

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_THEATRICAL_DAYS,
                        default=options.get(
                            CONF_THEATRICAL_DAYS,
                            DEFAULT_THEATRICAL_DAYS,
                        ),
                    ): _number_selector(
                        MIN_LOOKAHEAD_DAYS,
                        MAX_LOOKAHEAD_DAYS,
                    ),
                    vol.Required(
                        CONF_DIGITAL_DAYS,
                        default=options.get(
                            CONF_DIGITAL_DAYS,
                            DEFAULT_DIGITAL_DAYS,
                        ),
                    ): _number_selector(
                        MIN_LOOKAHEAD_DAYS,
                        MAX_LOOKAHEAD_DAYS,
                    ),
                    vol.Required(
                        CONF_TV_DAYS,
                        default=options.get(
                            CONF_TV_DAYS,
                            DEFAULT_TV_DAYS,
                        ),
                    ): _number_selector(
                        MIN_LOOKAHEAD_DAYS,
                        MAX_LOOKAHEAD_DAYS,
                    ),
                    vol.Required(
                        CONF_REFRESH_INTERVAL,
                        default=options.get(
                            CONF_REFRESH_INTERVAL,
                            DEFAULT_REFRESH_INTERVAL,
                        ),
                    ): _number_selector(
                        MIN_REFRESH_INTERVAL,
                        MAX_REFRESH_INTERVAL,
                    ),
                }
            ),
        )
