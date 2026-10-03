from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import (
    API_BASE,
    CONF_API_TOKEN,
    CONF_REGION,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def test_tmdb_connection(
    hass: HomeAssistant, api_token: str
) -> None:
    """Validate a TMDB Read Access Token."""
    session = async_get_clientsession(hass)
    async with session.get(
        f"{API_BASE}/configuration",
        headers={
            "Authorization": f"Bearer {api_token}",
            "accept": "application/json",
        },
        timeout=15,
    ) as response:
        if response.status != 200:
            raise RuntimeError(
                f"TMDB returned HTTP {response.status}"
            )


class EntertainmentCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch Entertainment Releases data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.api_token = entry.data[CONF_API_TOKEN]
        self.region = entry.data.get(CONF_REGION, "US")

        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                hours=DEFAULT_SCAN_INTERVAL_HOURS
            ),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        today = dt_util.now().date().isoformat()

        try:
            theatrical = await self._discover_movies(today, "3")
            digital = await self._discover_movies(today, "4")
            tv = await self._discover_tv(today)
        except Exception as err:
            raise UpdateFailed(
                f"Unable to retrieve entertainment releases: {err}"
            ) from err

        return {
            "date": today,
            "region": self.region,
            "theatrical": theatrical,
            "digital": digital,
            "tv": tv,
        }

    async def _request(
        self, endpoint: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)

        async with session.get(
            f"{API_BASE}{endpoint}",
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "accept": "application/json",
            },
            params=params,
            timeout=30,
        ) as response:
            if response.status != 200:
                body = await response.text()
                raise RuntimeError(
                    f"TMDB HTTP {response.status}: {body[:250]}"
                )
            return await response.json()

    async def _discover_movies(
        self, day: str, release_type: str
    ) -> list[dict[str, Any]]:
        data = await self._request(
            "/discover/movie",
            {
                "include_adult": "false",
                "include_video": "false",
                "language": "en-US",
                "page": 1,
                "region": self.region,
                "release_date.gte": day,
                "release_date.lte": day,
                "sort_by": "popularity.desc",
                "with_release_type": release_type,
            },
        )

        return [
            {
                "id": item["id"],
                "title": item.get("title"),
                "overview": item.get("overview"),
                "poster_path": item.get("poster_path"),
                "backdrop_path": item.get("backdrop_path"),
                "release_date": item.get("release_date"),
                "vote_average": item.get("vote_average"),
                "vote_count": item.get("vote_count"),
                "popularity": item.get("popularity"),
                "tmdb_url": (
                    f"https://www.themoviedb.org/movie/{item['id']}"
                ),
            }
            for item in data.get("results", [])
        ]

    async def _discover_tv(self, day: str) -> list[dict[str, Any]]:
        data = await self._request(
            "/discover/tv",
            {
                "include_adult": "false",
                "language": "en-US",
                "page": 1,
                "air_date.gte": day,
                "air_date.lte": day,
                "sort_by": "popularity.desc",
            },
        )

        return [
            {
                "id": item["id"],
                "name": item.get("name"),
                "overview": item.get("overview"),
                "poster_path": item.get("poster_path"),
                "backdrop_path": item.get("backdrop_path"),
                "first_air_date": item.get("first_air_date"),
                "vote_average": item.get("vote_average"),
                "vote_count": item.get("vote_count"),
                "popularity": item.get("popularity"),
                "tmdb_url": (
                    f"https://www.themoviedb.org/tv/{item['id']}"
                ),
            }
            for item in data.get("results", [])
        ]
