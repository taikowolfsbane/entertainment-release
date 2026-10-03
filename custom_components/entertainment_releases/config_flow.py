from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import (
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector

from .const import (
    CONF_API_TOKEN,
    CONF_DIGITAL_DAYS,
    CONF_MOVIE_LANGUAGE,
    CONF_MOVIE_MIN_SCORE,
    CONF_REFRESH_INTERVAL,
    CONF_REGION,
    CONF_THEATRICAL_DAYS,
    CONF_TV_DAYS,
    CONF_TV_GENRES,
    CONF_TV_LANGUAGE,
    CONF_TV_PROVIDERS,
    DEFAULT_DIGITAL_DAYS,
    DEFAULT_MOVIE_LANGUAGE,
    DEFAULT_MOVIE_MIN_SCORE,
    DEFAULT_REFRESH_INTERVAL,
    DEFAULT_REGION,
    DEFAULT_THEATRICAL_DAYS,
    DEFAULT_TV_DAYS,
    DEFAULT_TV_GENRES,
    DEFAULT_TV_LANGUAGE,
    DEFAULT_TV_PROVIDERS,
    DOMAIN,
    MAX_LOOKAHEAD_DAYS,
    MAX_MOVIE_SCORE,
    MAX_REFRESH_INTERVAL,
    MIN_LOOKAHEAD_DAYS,
    MIN_MOVIE_SCORE,
    MIN_REFRESH_INTERVAL,
)
from .coordinator import (
    get_tv_genres,
    get_tv_watch_providers,
    test_tmdb_connection,
)


def _number_selector(
    minimum: float,
    maximum: float,
    step: float = 1,
) -> selector.NumberSelector:
    """Create a number box selector."""
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=minimum,
            max=maximum,
            step=step,
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
                        CONF_MOVIE_LANGUAGE: DEFAULT_MOVIE_LANGUAGE,
                        CONF_MOVIE_MIN_SCORE: DEFAULT_MOVIE_MIN_SCORE,
                        CONF_TV_PROVIDERS: DEFAULT_TV_PROVIDERS,
                        CONF_TV_GENRES: DEFAULT_TV_GENRES,
                        CONF_TV_LANGUAGE: DEFAULT_TV_LANGUAGE,
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
                    CONF_THEATRICAL_DAYS: int(
                        user_input[CONF_THEATRICAL_DAYS]
                    ),
                    CONF_DIGITAL_DAYS: int(
                        user_input[CONF_DIGITAL_DAYS]
                    ),
                    CONF_TV_DAYS: int(
                        user_input[CONF_TV_DAYS]
                    ),
                    CONF_REFRESH_INTERVAL: int(
                        user_input[CONF_REFRESH_INTERVAL]
                    ),
                    CONF_MOVIE_LANGUAGE: str(
                        user_input[CONF_MOVIE_LANGUAGE]
                    ).strip().lower(),
                    CONF_MOVIE_MIN_SCORE: float(
                        user_input[CONF_MOVIE_MIN_SCORE]
                    ),
                    CONF_TV_PROVIDERS: list(
                        user_input.get(CONF_TV_PROVIDERS, [])
                    ),
                    CONF_TV_GENRES: list(
                        user_input.get(CONF_TV_GENRES, [])
                    ),
                    CONF_TV_LANGUAGE: str(
                        user_input[CONF_TV_LANGUAGE]
                    ).strip().lower(),
                },
            )

        options = self.config_entry.options
        api_token = self.config_entry.data[CONF_API_TOKEN]
        region = self.config_entry.data.get(CONF_REGION, DEFAULT_REGION)

        try:
            providers = await get_tv_watch_providers(
                self.hass,
                api_token,
                region,
            )
        except Exception:
            providers = {}

        try:
            genres = await get_tv_genres(
                self.hass,
                api_token,
            )
        except Exception:
            genres = {}

        provider_defaults = [
            provider_id
            for provider_id in options.get(
                CONF_TV_PROVIDERS,
                DEFAULT_TV_PROVIDERS,
            )
            if not providers or provider_id in providers
        ]

        genre_defaults = [
            genre_id
            for genre_id in options.get(
                CONF_TV_GENRES,
                DEFAULT_TV_GENRES,
            )
            if not genres or genre_id in genres
        ]

        schema: dict[Any, Any] = {
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
            vol.Required(
                CONF_MOVIE_LANGUAGE,
                default=options.get(
                    CONF_MOVIE_LANGUAGE,
                    DEFAULT_MOVIE_LANGUAGE,
                ),
            ): str,
            vol.Required(
                CONF_MOVIE_MIN_SCORE,
                default=options.get(
                    CONF_MOVIE_MIN_SCORE,
                    DEFAULT_MOVIE_MIN_SCORE,
                ),
            ): _number_selector(
                MIN_MOVIE_SCORE,
                MAX_MOVIE_SCORE,
                0.5,
            ),
            vol.Required(
                CONF_TV_LANGUAGE,
                default=options.get(
                    CONF_TV_LANGUAGE,
                    DEFAULT_TV_LANGUAGE,
                ),
            ): str,
        }

        if providers:
            schema[
                vol.Optional(
                    CONF_TV_PROVIDERS,
                    default=provider_defaults,
                )
            ] = cv.multi_select(providers)

        if genres:
            schema[
                vol.Optional(
                    CONF_TV_GENRES,
                    default=genre_defaults,
                )
            ] = cv.multi_select(genres)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
        )
