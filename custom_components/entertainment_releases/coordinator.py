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
    CONF_DIGITAL_DAYS,
    CONF_REFRESH_INTERVAL,
    CONF_REGION,
    CONF_THEATRICAL_DAYS,
    CONF_TV_DAYS,
    DEFAULT_DIGITAL_DAYS,
    DEFAULT_REFRESH_INTERVAL,
    DEFAULT_THEATRICAL_DAYS,
    DEFAULT_TV_DAYS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def test_tmdb_connection(
    hass: HomeAssistant,
    api_token: str,
) -> None:
    """Validate a TMDB API Read Access Token."""
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
    """Fetch and coordinate Entertainment Releases data."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.api_token = entry.data[CONF_API_TOKEN]
        self.region = entry.data.get(CONF_REGION, "US")

        self.theatrical_days = int(
            entry.options.get(
                CONF_THEATRICAL_DAYS,
                DEFAULT_THEATRICAL_DAYS,
            )
        )
        self.digital_days = int(
            entry.options.get(
                CONF_DIGITAL_DAYS,
                DEFAULT_DIGITAL_DAYS,
            )
        )
        self.tv_days = int(
            entry.options.get(
                CONF_TV_DAYS,
                DEFAULT_TV_DAYS,
            )
        )

        refresh_interval = int(
            entry.options.get(
                CONF_REFRESH_INTERVAL,
                DEFAULT_REFRESH_INTERVAL,
            )
        )

        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=refresh_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch release data from TMDB."""
        today_date = dt_util.now().date()
        today = today_date.isoformat()

        theatrical_end = (
            today_date + timedelta(days=self.theatrical_days - 1)
        ).isoformat()
        digital_end = (
            today_date + timedelta(days=self.digital_days - 1)
        ).isoformat()
        tv_end = (
            today_date + timedelta(days=self.tv_days - 1)
        ).isoformat()

        try:
            theatrical = await self._discover_movies(
                today,
                theatrical_end,
                "3",
                new_theatrical_only=True,
            )
            digital = await self._discover_movies(
                today,
                digital_end,
                "4",
            )
            tv = await self._discover_tv(
                today,
                tv_end,
            )
        except Exception as err:
            raise UpdateFailed(
                f"Unable to retrieve entertainment releases: {err}"
            ) from err

        return {
            "date": today,
            "region": self.region,
            "theatrical_days": self.theatrical_days,
            "digital_days": self.digital_days,
            "tv_days": self.tv_days,
            "theatrical": theatrical,
            "digital": digital,
            "tv": tv,
        }

    async def _request(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Make an authenticated TMDB request."""
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
                raise RuntimeError(
                    f"TMDB returned HTTP {response.status}"
                )

            return await response.json()

    async def _request_all_pages(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Request all TMDB result pages for a query."""
        first_params = dict(params)
        first_params["page"] = 1

        first_page = await self._request(endpoint, first_params)
        results = list(first_page.get("results", []))

        total_pages = min(
            int(first_page.get("total_pages", 1)),
            500,
        )

        for page in range(2, total_pages + 1):
            page_params = dict(params)
            page_params["page"] = page
            page_data = await self._request(endpoint, page_params)
            results.extend(page_data.get("results", []))

        return results

    async def _discover_movies(
        self,
        start: str,
        end: str,
        release_type: str,
        new_theatrical_only: bool = False,
    ) -> list[dict[str, Any]]:
        """Find movies released in a date range."""
        results = await self._request_all_pages(
            "/discover/movie",
            {
                "include_adult": "false",
                "include_video": "false",
                "language": "en-US",
                "region": self.region,
                "release_date.gte": start,
                "release_date.lte": end,
                "sort_by": "release_date.asc",
                "with_release_type": release_type,
            },
        )

        if new_theatrical_only:
            filtered_results: list[dict[str, Any]] = []

            for item in results:
                release_date = item.get("release_date")

                if not release_date:
                    continue

                if await self._is_first_theatrical_release(
                    item["id"],
                    release_date,
                ):
                    filtered_results.append(item)

            results = filtered_results

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
            for item in results
        ]

    async def _is_first_theatrical_release(
        self,
        movie_id: int,
        candidate_date: str,
    ) -> bool:
        """Return True when candidate date is the first theatrical release.

        TMDB release types:
        2 = Theatrical (limited)
        3 = Theatrical

        We inspect release history for the configured region and compare the
        candidate date with the earliest limited or standard theatrical date.
        Later re-releases, anniversary runs, and restorations are excluded.
        """
        data = await self._request(
            f"/movie/{movie_id}/release_dates",
            {},
        )

        theatrical_dates: list[str] = []

        for country in data.get("results", []):
            if country.get("iso_3166_1") != self.region:
                continue

            for release in country.get("release_dates", []):
                if release.get("type") not in (2, 3):
                    continue

                raw_date = release.get("release_date")
                if not raw_date:
                    continue

                # TMDB returns ISO timestamps for release-history records.
                # Compare only the calendar date.
                theatrical_dates.append(raw_date[:10])

        if not theatrical_dates:
            # If release history is incomplete, keep the discover result
            # rather than silently discarding a potentially valid new title.
            return True

        earliest_theatrical = min(theatrical_dates)
        return candidate_date == earliest_theatrical

    async def _discover_tv(
        self,
        start: str,
        end: str,
    ) -> list[dict[str, Any]]:
        """Find TV shows airing in a date range."""
        results = await self._request_all_pages(
            "/discover/tv",
            {
                "include_adult": "false",
                "language": "en-US",
                "air_date.gte": start,
                "air_date.lte": end,
                "sort_by": "first_air_date.asc",
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
            for item in results
        ]
