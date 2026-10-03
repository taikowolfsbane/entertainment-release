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
)

_LOGGER = logging.getLogger(__name__)


def _headers(api_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_token}",
        "accept": "application/json",
    }


async def test_tmdb_connection(
    hass: HomeAssistant,
    api_token: str,
) -> None:
    """Validate a TMDB API Read Access Token."""
    session = async_get_clientsession(hass)

    async with session.get(
        f"{API_BASE}/configuration",
        headers=_headers(api_token),
        timeout=15,
    ) as response:
        if response.status != 200:
            raise RuntimeError(
                f"TMDB returned HTTP {response.status}"
            )


async def get_tv_watch_providers(
    hass: HomeAssistant,
    api_token: str,
    region: str,
) -> dict[str, str]:
    """Return available TV streaming providers for a region."""
    session = async_get_clientsession(hass)

    async with session.get(
        f"{API_BASE}/watch/providers/tv",
        headers=_headers(api_token),
        params={
            "language": "en-US",
            "watch_region": region,
        },
        timeout=30,
    ) as response:
        if response.status != 200:
            raise RuntimeError(
                f"TMDB returned HTTP {response.status}"
            )

        data = await response.json()

    results = sorted(
        data.get("results", []),
        key=lambda item: (
            item.get("display_priority", 9999),
            item.get("provider_name", ""),
        ),
    )

    return {
        str(item["provider_id"]): item["provider_name"]
        for item in results
        if item.get("provider_id") is not None
        and item.get("provider_name")
    }


async def get_tv_genres(
    hass: HomeAssistant,
    api_token: str,
) -> dict[str, str]:
    """Return TMDB TV genres."""
    session = async_get_clientsession(hass)

    async with session.get(
        f"{API_BASE}/genre/tv/list",
        headers=_headers(api_token),
        params={"language": "en-US"},
        timeout=30,
    ) as response:
        if response.status != 200:
            raise RuntimeError(
                f"TMDB returned HTTP {response.status}"
            )

        data = await response.json()

    return {
        str(item["id"]): item["name"]
        for item in data.get("genres", [])
        if item.get("id") is not None and item.get("name")
    }


class EntertainmentCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch and coordinate Entertainment Releases data."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.api_token = entry.data[CONF_API_TOKEN]
        self.region = entry.data.get(CONF_REGION, DEFAULT_REGION)

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

        self.movie_language = str(
            entry.options.get(
                CONF_MOVIE_LANGUAGE,
                DEFAULT_MOVIE_LANGUAGE,
            )
        ).lower()

        self.movie_min_score = float(
            entry.options.get(
                CONF_MOVIE_MIN_SCORE,
                DEFAULT_MOVIE_MIN_SCORE,
            )
        )

        self.tv_language = str(
            entry.options.get(
                CONF_TV_LANGUAGE,
                DEFAULT_TV_LANGUAGE,
            )
        ).lower()

        self.tv_providers = [
            str(provider)
            for provider in entry.options.get(
                CONF_TV_PROVIDERS,
                DEFAULT_TV_PROVIDERS,
            )
        ]

        self.tv_genres = [
            str(genre)
            for genre in entry.options.get(
                CONF_TV_GENRES,
                DEFAULT_TV_GENRES,
            )
        ]

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
                first_release_only=True,
                first_release_types=(3,),
                apply_relevance_filter=True,
            )

            digital = await self._discover_movies(
                today,
                digital_end,
                "4",
                first_release_only=True,
                first_release_types=(4,),
                apply_relevance_filter=False,
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
            "movie_language": self.movie_language,
            "movie_min_score": self.movie_min_score,
            "tv_language": self.tv_language,
            "tv_providers": self.tv_providers,
            "tv_genres": self.tv_genres,
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
            headers=_headers(self.api_token),
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
        *,
        first_release_only: bool,
        first_release_types: tuple[int, ...],
        apply_relevance_filter: bool,
    ) -> list[dict[str, Any]]:
        """Find movies released in a date range.

        TMDB discover is used only to find candidates. The actual regional
        release date is then derived from each movie's release history so the
        integration does not accidentally display the movie's primary/global
        release date or a later re-release as a new release.
        """
        params: dict[str, Any] = {
            "include_adult": "false",
            "include_video": "false",
            "language": "en-US",
            "region": self.region,
            "release_date.gte": start,
            "release_date.lte": end,
            "sort_by": "popularity.desc",
            "with_release_type": release_type,
        }

        if self.movie_language:
            params["with_original_language"] = self.movie_language

        results = await self._request_all_pages(
            "/discover/movie",
            params,
        )

        filtered_results: list[dict[str, Any]] = []

        for item in results:
            regional_dates = await self._get_regional_release_dates(
                item["id"],
                first_release_types,
            )

            if first_release_only:
                if not regional_dates:
                    # Without release-history confirmation, do not label an
                    # old or ambiguous title as a new release.
                    continue

                actual_release_date = min(regional_dates)

                if not (start <= actual_release_date <= end):
                    continue
            else:
                actual_release_date = item.get("release_date")

            if not actual_release_date:
                continue

            if apply_relevance_filter:
                # Apply the score threshold only once the movie has reached
                # its release date. Future unrated releases remain visible.
                if actual_release_date <= start:
                    vote_average = float(item.get("vote_average") or 0)
                    if vote_average < self.movie_min_score:
                        continue

            item = dict(item)
            item["_regional_release_date"] = actual_release_date
            filtered_results.append(item)

        filtered_results.sort(
            key=lambda item: (
                item.get("_regional_release_date") or "9999-12-31",
                -float(item.get("popularity") or 0),
            )
        )

        return [
            {
                "id": item["id"],
                "title": item.get("title"),
                "overview": item.get("overview"),
                "poster_path": item.get("poster_path"),
                "poster_url": (
                    "https://image.tmdb.org/t/p/w342"
                    f"{item.get('poster_path')}"
                    if item.get("poster_path")
                    else None
                ),
                "backdrop_path": item.get("backdrop_path"),
                "release_date": item.get("_regional_release_date"),
                "vote_average": item.get("vote_average"),
                "vote_count": item.get("vote_count"),
                "popularity": item.get("popularity"),
                "original_language": item.get("original_language"),
                "tmdb_url": (
                    f"https://www.themoviedb.org/movie/{item['id']}"
                ),
            }
            for item in filtered_results
        ]

    async def _get_regional_release_dates(
        self,
        movie_id: int,
        release_types: tuple[int, ...],
    ) -> list[str]:
        """Return regional calendar dates for the requested release types."""
        data = await self._request(
            f"/movie/{movie_id}/release_dates",
            {},
        )

        dates: set[str] = set()

        for country in data.get("results", []):
            if country.get("iso_3166_1") != self.region:
                continue

            for release in country.get("release_dates", []):
                if release.get("type") not in release_types:
                    continue

                raw_date = release.get("release_date")
                if raw_date:
                    dates.add(raw_date[:10])

        return sorted(dates)

    async def _discover_tv(
        self,
        start: str,
        end: str,
    ) -> list[dict[str, Any]]:
        """Find relevant TV shows in the configured streaming services."""
        params: dict[str, Any] = {
            "include_adult": "false",
            "include_null_first_air_dates": "false",
            "language": "en-US",
            "air_date.gte": start,
            "air_date.lte": end,
            "sort_by": "popularity.desc",
            "watch_region": self.region,
            "with_watch_monetization_types": "flatrate",
            # TMDB type 2 = Miniseries and 4 = Scripted.
            # The pipe gives us OR behavior.
            "with_type": "2|4",
        }

        if self.tv_language:
            params["with_original_language"] = self.tv_language

        if self.tv_providers:
            params["with_watch_providers"] = "|".join(
                self.tv_providers
            )

        if self.tv_genres:
            # Pipe-separated genre IDs are OR logic in TMDB discover.
            params["with_genres"] = "|".join(self.tv_genres)

        results = await self._request_all_pages(
            "/discover/tv",
            params,
        )

        results.sort(
            key=lambda item: (
                -float(item.get("popularity") or 0),
                item.get("name") or "",
            )
        )

        return [
            {
                "id": item["id"],
                "name": item.get("name"),
                "overview": item.get("overview"),
                "poster_path": item.get("poster_path"),
                "poster_url": (
                    "https://image.tmdb.org/t/p/w342"
                    f"{item.get('poster_path')}"
                    if item.get("poster_path")
                    else None
                ),
                "backdrop_path": item.get("backdrop_path"),
                "first_air_date": item.get("first_air_date"),
                "vote_average": item.get("vote_average"),
                "vote_count": item.get("vote_count"),
                "popularity": item.get("popularity"),
                "original_language": item.get("original_language"),
                "genre_ids": item.get("genre_ids", []),
                "origin_country": item.get("origin_country", []),
                "tmdb_url": (
                    f"https://www.themoviedb.org/tv/{item['id']}"
                ),
            }
            for item in results
        ]
