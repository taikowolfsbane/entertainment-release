from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult, OptionsFlowWithReload
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector

from .const import *
from .coordinator import (
    get_countries,
    get_languages,
    get_movie_genres,
    get_tv_genres,
    get_tv_watch_providers,
    test_tmdb_connection,
)


def _number_box(minimum: float, maximum: float, step: float = 1):
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
    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
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
                    options={},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_TOKEN): str,
                    vol.Optional(CONF_REGION, default=DEFAULT_REGION): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "EntertainmentReleasesOptionsFlow":
        return EntertainmentReleasesOptionsFlow()


class EntertainmentReleasesOptionsFlow(OptionsFlowWithReload):
    def __init__(self) -> None:
        self._pending: dict[str, Any] = {}
        self._countries: dict[str, str] = {}
        self._languages: dict[str, str] = {}
        self._movie_genres: dict[str, str] = {}
        self._tv_genres: dict[str, str] = {}

    async def _load_common_lists(self) -> None:
        token = self.config_entry.data[CONF_API_TOKEN]
        if not self._countries:
            self._countries = await get_countries(self.hass, token)
        if not self._languages:
            self._languages = await get_languages(self.hass, token)
        if not self._movie_genres:
            self._movie_genres = await get_movie_genres(self.hass, token)
        if not self._tv_genres:
            self._tv_genres = await get_tv_genres(self.hass, token)

    def _current(self, key: str, default: Any) -> Any:
        if key in self._pending:
            return self._pending[key]
        return self.config_entry.options.get(key, default)

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        return await self.async_step_theatrical()

    async def async_step_theatrical(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        await self._load_common_lists()
        if user_input is not None:
            self._pending.update(user_input)
            return await self.async_step_digital()

        return self.async_show_form(
            step_id="theatrical",
            data_schema=vol.Schema({
                vol.Required(CONF_THEATRICAL_COUNTRY, default=self._current(CONF_THEATRICAL_COUNTRY, DEFAULT_THEATRICAL_COUNTRY)): vol.In(self._countries),
                vol.Required(CONF_THEATRICAL_RELEASE_TYPES, default=self._current(CONF_THEATRICAL_RELEASE_TYPES, DEFAULT_THEATRICAL_RELEASE_TYPES)): cv.multi_select(RELEASE_TYPES),
                vol.Required(CONF_THEATRICAL_DAYS, default=self._current(CONF_THEATRICAL_DAYS, DEFAULT_THEATRICAL_DAYS)): _number_box(1, 30),
                vol.Optional(CONF_THEATRICAL_GENRES, default=self._current(CONF_THEATRICAL_GENRES, DEFAULT_THEATRICAL_GENRES)): cv.multi_select(self._movie_genres),
                vol.Optional(
                    CONF_THEATRICAL_CERTIFICATION,
                    default=self._current(
                        CONF_THEATRICAL_CERTIFICATION,
                        DEFAULT_THEATRICAL_CERTIFICATION,
                    ),
                ): cv.multi_select(US_CERTIFICATIONS),
                vol.Required(CONF_THEATRICAL_LANGUAGE, default=self._current(CONF_THEATRICAL_LANGUAGE, DEFAULT_THEATRICAL_LANGUAGE)): vol.In(self._languages),
                vol.Required(CONF_THEATRICAL_MIN_SCORE, default=self._current(CONF_THEATRICAL_MIN_SCORE, DEFAULT_THEATRICAL_MIN_SCORE)): _number_box(0, 10, 0.5),
                vol.Required(CONF_THEATRICAL_MIN_VOTES, default=self._current(CONF_THEATRICAL_MIN_VOTES, DEFAULT_THEATRICAL_MIN_VOTES)): _number_box(0, 10000, 1),
                vol.Required(CONF_THEATRICAL_RUNTIME_MIN, default=self._current(CONF_THEATRICAL_RUNTIME_MIN, DEFAULT_THEATRICAL_RUNTIME_MIN)): _number_box(0, 500, 1),
                vol.Required(CONF_THEATRICAL_RUNTIME_MAX, default=self._current(CONF_THEATRICAL_RUNTIME_MAX, DEFAULT_THEATRICAL_RUNTIME_MAX)): _number_box(0, 500, 1),
                vol.Required(
                    CONF_THEATRICAL_EXCLUDE_RERELEASES,
                    default=self._current(
                        CONF_THEATRICAL_EXCLUDE_RERELEASES,
                        DEFAULT_THEATRICAL_EXCLUDE_RERELEASES,
                    ),
                ): bool,
                vol.Required(
                    CONF_THEATRICAL_SORT_BY_RELEASE_DATE,
                    default=self._current(
                        CONF_THEATRICAL_SORT_BY_RELEASE_DATE,
                        DEFAULT_THEATRICAL_SORT_BY_RELEASE_DATE,
                    ),
                ): bool,
            }),
        )

    async def async_step_digital(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        await self._load_common_lists()
        if user_input is not None:
            self._pending.update(user_input)
            return await self.async_step_tv()

        return self.async_show_form(
            step_id="digital",
            data_schema=vol.Schema({
                vol.Required(CONF_DIGITAL_COUNTRY, default=self._current(CONF_DIGITAL_COUNTRY, DEFAULT_DIGITAL_COUNTRY)): vol.In(self._countries),
                vol.Required(CONF_DIGITAL_RELEASE_TYPES, default=self._current(CONF_DIGITAL_RELEASE_TYPES, DEFAULT_DIGITAL_RELEASE_TYPES)): cv.multi_select(RELEASE_TYPES),
                vol.Required(CONF_DIGITAL_DAYS, default=self._current(CONF_DIGITAL_DAYS, DEFAULT_DIGITAL_DAYS)): _number_box(1, 30),
                vol.Optional(CONF_DIGITAL_GENRES, default=self._current(CONF_DIGITAL_GENRES, DEFAULT_DIGITAL_GENRES)): cv.multi_select(self._movie_genres),
                vol.Optional(
                    CONF_DIGITAL_CERTIFICATION,
                    default=self._current(
                        CONF_DIGITAL_CERTIFICATION,
                        DEFAULT_DIGITAL_CERTIFICATION,
                    ),
                ): cv.multi_select(US_CERTIFICATIONS),
                vol.Required(CONF_DIGITAL_LANGUAGE, default=self._current(CONF_DIGITAL_LANGUAGE, DEFAULT_DIGITAL_LANGUAGE)): vol.In(self._languages),
                vol.Required(CONF_DIGITAL_MIN_SCORE, default=self._current(CONF_DIGITAL_MIN_SCORE, DEFAULT_DIGITAL_MIN_SCORE)): _number_box(0, 10, 0.5),
                vol.Required(CONF_DIGITAL_MIN_VOTES, default=self._current(CONF_DIGITAL_MIN_VOTES, DEFAULT_DIGITAL_MIN_VOTES)): _number_box(0, 10000, 1),
                vol.Required(CONF_DIGITAL_RUNTIME_MIN, default=self._current(CONF_DIGITAL_RUNTIME_MIN, DEFAULT_DIGITAL_RUNTIME_MIN)): _number_box(0, 500, 1),
                vol.Required(CONF_DIGITAL_RUNTIME_MAX, default=self._current(CONF_DIGITAL_RUNTIME_MAX, DEFAULT_DIGITAL_RUNTIME_MAX)): _number_box(0, 500, 1),
            }),
        )

    async def async_step_tv(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        await self._load_common_lists()
        if user_input is not None:
            self._pending.update(user_input)
            return await self.async_step_general()

        country = self._current(CONF_TV_COUNTRY, DEFAULT_TV_COUNTRY)
        providers = await get_tv_watch_providers(
            self.hass,
            self.config_entry.data[CONF_API_TOKEN],
            country,
        )
        provider_defaults = [
            p for p in self._current(CONF_TV_PROVIDERS, DEFAULT_TV_PROVIDERS)
            if p in providers
        ]

        return self.async_show_form(
            step_id="tv",
            data_schema=vol.Schema({
                vol.Required(CONF_TV_COUNTRY, default=country): vol.In(self._countries),
                vol.Required(CONF_TV_DAYS, default=self._current(CONF_TV_DAYS, DEFAULT_TV_DAYS)): _number_box(1, 30),
                vol.Optional(CONF_TV_PROVIDERS, default=provider_defaults): cv.multi_select(providers),
                vol.Optional(CONF_TV_GENRES, default=self._current(CONF_TV_GENRES, DEFAULT_TV_GENRES)): cv.multi_select(self._tv_genres),
                vol.Optional(CONF_TV_TYPES, default=self._current(CONF_TV_TYPES, DEFAULT_TV_TYPES)): cv.multi_select(TV_TYPES),
                vol.Required(CONF_TV_LANGUAGE, default=self._current(CONF_TV_LANGUAGE, DEFAULT_TV_LANGUAGE)): vol.In(self._languages),
                vol.Required(CONF_TV_MIN_SCORE, default=self._current(CONF_TV_MIN_SCORE, DEFAULT_TV_MIN_SCORE)): _number_box(0, 10, 0.5),
                vol.Required(CONF_TV_MIN_VOTES, default=self._current(CONF_TV_MIN_VOTES, DEFAULT_TV_MIN_VOTES)): _number_box(0, 10000, 1),
                vol.Required(CONF_TV_RUNTIME_MIN, default=self._current(CONF_TV_RUNTIME_MIN, DEFAULT_TV_RUNTIME_MIN)): _number_box(0, 500, 1),
                vol.Required(CONF_TV_RUNTIME_MAX, default=self._current(CONF_TV_RUNTIME_MAX, DEFAULT_TV_RUNTIME_MAX)): _number_box(0, 500, 1),
            }),
        )

    async def async_step_general(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._pending.update(user_input)
            return self.async_create_entry(title="", data=self._pending)

        return self.async_show_form(
            step_id="general",
            data_schema=vol.Schema({
                vol.Required(CONF_REFRESH_INTERVAL, default=self._current(CONF_REFRESH_INTERVAL, DEFAULT_REFRESH_INTERVAL)): _number_box(1, 24),
            }),
        )
