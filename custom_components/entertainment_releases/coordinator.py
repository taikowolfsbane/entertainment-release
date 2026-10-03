from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import *

_LOGGER = logging.getLogger(__name__)


def _headers(api_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_token}",
        "accept": "application/json",
    }


async def _simple_get(
    hass: HomeAssistant,
    api_token: str,
    endpoint: str,
    params: dict[str, Any] | None = None,
):
    session = async_get_clientsession(hass)
    async with session.get(
        f"{API_BASE}{endpoint}",
        headers=_headers(api_token),
        params=params or {},
        timeout=30,
    ) as response:
        if response.status != 200:
            raise RuntimeError(f"TMDB returned HTTP {response.status}")
        return await response.json()


async def test_tmdb_connection(hass: HomeAssistant, api_token: str) -> None:
    await _simple_get(hass, api_token, "/configuration")


async def get_countries(hass: HomeAssistant, api_token: str) -> dict[str, str]:
    data = await _simple_get(hass, api_token, "/configuration/countries")
    return {
        item["iso_3166_1"]: item.get("english_name") or item["iso_3166_1"]
        for item in data
        if item.get("iso_3166_1")
    }


async def get_languages(hass: HomeAssistant, api_token: str) -> dict[str, str]:
    data = await _simple_get(hass, api_token, "/configuration/languages")
    return {
        item["iso_639_1"]: item.get("english_name") or item.get("name") or item["iso_639_1"]
        for item in data
        if item.get("iso_639_1")
    }


async def get_movie_genres(hass: HomeAssistant, api_token: str) -> dict[str, str]:
    data = await _simple_get(
        hass, api_token, "/genre/movie/list", {"language": "en-US"}
    )
    return {str(item["id"]): item["name"] for item in data.get("genres", [])}


async def get_tv_genres(hass: HomeAssistant, api_token: str) -> dict[str, str]:
    data = await _simple_get(
        hass, api_token, "/genre/tv/list", {"language": "en-US"}
    )
    return {str(item["id"]): item["name"] for item in data.get("genres", [])}


async def get_tv_watch_providers(
    hass: HomeAssistant,
    api_token: str,
    region: str,
) -> dict[str, str]:
    data = await _simple_get(
        hass,
        api_token,
        "/watch/providers/tv",
        {"language": "en-US", "watch_region": region},
    )
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
        if item.get("provider_id") is not None and item.get("provider_name")
    }


class EntertainmentCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.api_token = entry.data[CONF_API_TOKEN]
        self.base_region = entry.data.get(CONF_REGION, DEFAULT_REGION)
        self.options = entry.options

        refresh_interval = int(
            self.options.get(CONF_REFRESH_INTERVAL, DEFAULT_REFRESH_INTERVAL)
        )

        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=refresh_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        today_date = dt_util.now().date()
        today = today_date.isoformat()

        try:
            theatrical_days = int(
                self.options.get(CONF_THEATRICAL_DAYS, DEFAULT_THEATRICAL_DAYS)
            )
            digital_days = int(
                self.options.get(CONF_DIGITAL_DAYS, DEFAULT_DIGITAL_DAYS)
            )
            tv_days = int(self.options.get(CONF_TV_DAYS, DEFAULT_TV_DAYS))

            theatrical = await self._discover_movie_category(
                "theatrical",
                today,
                (today_date + timedelta(days=theatrical_days - 1)).isoformat(),
            )
            digital = await self._discover_movie_category(
                "digital",
                today,
                (today_date + timedelta(days=digital_days - 1)).isoformat(),
            )
            tv = await self._discover_tv(
                today,
                (today_date + timedelta(days=tv_days - 1)).isoformat(),
            )
        except Exception as err:
            raise UpdateFailed(
                f"Unable to retrieve entertainment releases: {err}"
            ) from err

        return {
            "date": today,
            "theatrical": theatrical,
            "digital": digital,
            "tv": tv,
        }

    async def _request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)
        async with session.get(
            f"{API_BASE}{endpoint}",
            headers=_headers(self.api_token),
            params=params,
            timeout=30,
        ) as response:
            if response.status != 200:
                raise RuntimeError(f"TMDB returned HTTP {response.status}")
            return await response.json()

    async def _request_all_pages(
        self, endpoint: str, params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        first = dict(params)
        first["page"] = 1
        page_data = await self._request(endpoint, first)
        results = list(page_data.get("results", []))
        total_pages = min(int(page_data.get("total_pages", 1)), 500)

        for page in range(2, total_pages + 1):
            page_params = dict(params)
            page_params["page"] = page
            data = await self._request(endpoint, page_params)
            results.extend(data.get("results", []))
        return results

    def _movie_filter_values(self, category: str) -> dict[str, Any]:
        if category == "theatrical":
            return {
                "country": self.options.get(CONF_THEATRICAL_COUNTRY, DEFAULT_THEATRICAL_COUNTRY),
                "release_types": self.options.get(CONF_THEATRICAL_RELEASE_TYPES, DEFAULT_THEATRICAL_RELEASE_TYPES),
                "genres": self.options.get(CONF_THEATRICAL_GENRES, DEFAULT_THEATRICAL_GENRES),
                "certification": self.options.get(CONF_THEATRICAL_CERTIFICATION, DEFAULT_THEATRICAL_CERTIFICATION),
                "language": self.options.get(CONF_THEATRICAL_LANGUAGE, DEFAULT_THEATRICAL_LANGUAGE),
                "min_score": self.options.get(CONF_THEATRICAL_MIN_SCORE, DEFAULT_THEATRICAL_MIN_SCORE),
                "min_votes": self.options.get(CONF_THEATRICAL_MIN_VOTES, DEFAULT_THEATRICAL_MIN_VOTES),
                "runtime_min": self.options.get(CONF_THEATRICAL_RUNTIME_MIN, DEFAULT_THEATRICAL_RUNTIME_MIN),
                "runtime_max": self.options.get(CONF_THEATRICAL_RUNTIME_MAX, DEFAULT_THEATRICAL_RUNTIME_MAX),
                "exclude_rereleases": self.options.get(
                    CONF_THEATRICAL_EXCLUDE_RERELEASES,
                    DEFAULT_THEATRICAL_EXCLUDE_RERELEASES,
                ),
            }
        return {
            "country": self.options.get(CONF_DIGITAL_COUNTRY, DEFAULT_DIGITAL_COUNTRY),
            "release_types": self.options.get(CONF_DIGITAL_RELEASE_TYPES, DEFAULT_DIGITAL_RELEASE_TYPES),
            "genres": self.options.get(CONF_DIGITAL_GENRES, DEFAULT_DIGITAL_GENRES),
            "certification": self.options.get(CONF_DIGITAL_CERTIFICATION, DEFAULT_DIGITAL_CERTIFICATION),
            "language": self.options.get(CONF_DIGITAL_LANGUAGE, DEFAULT_DIGITAL_LANGUAGE),
            "min_score": self.options.get(CONF_DIGITAL_MIN_SCORE, DEFAULT_DIGITAL_MIN_SCORE),
            "min_votes": self.options.get(CONF_DIGITAL_MIN_VOTES, DEFAULT_DIGITAL_MIN_VOTES),
            "runtime_min": self.options.get(CONF_DIGITAL_RUNTIME_MIN, DEFAULT_DIGITAL_RUNTIME_MIN),
            "runtime_max": self.options.get(CONF_DIGITAL_RUNTIME_MAX, DEFAULT_DIGITAL_RUNTIME_MAX),
        }

    async def _discover_movie_category(
        self,
        category: str,
        start: str,
        end: str,
    ) -> list[dict[str, Any]]:
        values = self._movie_filter_values(category)

        params: dict[str, Any] = {
            "include_adult": "false",
            "include_video": "false",
            "language": "en-US",
            "region": values["country"],
            "release_date.gte": start,
            "release_date.lte": end,
            "sort_by": "popularity.desc",
        }

        release_types = [str(v) for v in values["release_types"]]
        if release_types:
            params["with_release_type"] = "|".join(release_types)

        genres = [str(v) for v in values["genres"]]
        if genres:
            params["with_genres"] = "|".join(genres)

        certifications = [
            str(value).strip()
            for value in (values["certification"] or [])
            if str(value).strip()
        ]

        language = str(values["language"] or "").strip()
        if language:
            params["with_original_language"] = language

        min_score = float(values["min_score"] or 0)
        if min_score > 0:
            params["vote_average.gte"] = min_score

        min_votes = int(values["min_votes"] or 0)
        if min_votes > 0:
            params["vote_count.gte"] = min_votes

        runtime_min = int(values["runtime_min"] or 0)
        if runtime_min > 0:
            params["with_runtime.gte"] = runtime_min

        runtime_max = int(values["runtime_max"] or 0)
        if runtime_max > 0:
            params["with_runtime.lte"] = runtime_max

        if certifications:
            merged: dict[int, dict[str, Any]] = {}

            for certification in certifications:
                certification_params = dict(params)
                certification_params["certification_country"] = values["country"]
                certification_params["certification"] = certification

                certification_results = await self._request_all_pages(
                    "/discover/movie",
                    certification_params,
                )

                for item in certification_results:
                    movie_id = item.get("id")
                    if movie_id is not None:
                        merged[int(movie_id)] = item

            results = list(merged.values())
            results.sort(
                key=lambda item: -float(item.get("popularity") or 0)
            )
        else:
            results = await self._request_all_pages(
                "/discover/movie",
                params,
            )

        if (
            category == "theatrical"
            and bool(values.get("exclude_rereleases"))
        ):
            # TMDB can return an older title because a new regional theatrical
            # event matches the Discover query. When enabled, keep only movies
            # whose main TMDB release_date itself falls inside this configured
            # date window. This intentionally removes re-releases.
            results = [
                item
                for item in results
                if item.get("release_date")
                and start <= item["release_date"] <= end
            ]

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
                "release_date": item.get("release_date"),
                "vote_average": item.get("vote_average"),
                "vote_count": item.get("vote_count"),
                "popularity": item.get("popularity"),
                "genre_ids": item.get("genre_ids", []),
                "original_language": item.get("original_language"),
                "tmdb_url": f"https://www.themoviedb.org/movie/{item['id']}",
            }
            for item in results
        ]

    async def _discover_tv(self, start: str, end: str) -> list[dict[str, Any]]:
        country = self.options.get(CONF_TV_COUNTRY, DEFAULT_TV_COUNTRY)
        genres = [str(v) for v in self.options.get(CONF_TV_GENRES, DEFAULT_TV_GENRES)]
        providers = [str(v) for v in self.options.get(CONF_TV_PROVIDERS, DEFAULT_TV_PROVIDERS)]
        tv_types = [str(v) for v in self.options.get(CONF_TV_TYPES, DEFAULT_TV_TYPES)]

        params: dict[str, Any] = {
            "include_adult": "false",
            "include_null_first_air_dates": "false",
            "language": "en-US",
            "air_date.gte": start,
            "air_date.lte": end,
            "sort_by": "popularity.desc",
            "watch_region": country,
            "with_origin_country": country,
        }

        if genres:
            params["with_genres"] = "|".join(genres)

        language = str(
            self.options.get(CONF_TV_LANGUAGE, DEFAULT_TV_LANGUAGE) or ""
        ).strip()
        if language:
            params["with_original_language"] = language

        min_score = float(
            self.options.get(CONF_TV_MIN_SCORE, DEFAULT_TV_MIN_SCORE) or 0
        )
        if min_score > 0:
            params["vote_average.gte"] = min_score

        min_votes = int(
            self.options.get(CONF_TV_MIN_VOTES, DEFAULT_TV_MIN_VOTES) or 0
        )
        if min_votes > 0:
            params["vote_count.gte"] = min_votes

        runtime_min = int(
            self.options.get(CONF_TV_RUNTIME_MIN, DEFAULT_TV_RUNTIME_MIN) or 0
        )
        if runtime_min > 0:
            params["with_runtime.gte"] = runtime_min

        runtime_max = int(
            self.options.get(CONF_TV_RUNTIME_MAX, DEFAULT_TV_RUNTIME_MAX) or 0
        )
        if runtime_max > 0:
            params["with_runtime.lte"] = runtime_max

        if providers:
            params["with_watch_providers"] = "|".join(providers)
            params["with_watch_monetization_types"] = "flatrate"

        if tv_types:
            params["with_type"] = "|".join(tv_types)

        results = await self._request_all_pages("/discover/tv", params)

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
                "genre_ids": item.get("genre_ids", []),
                "origin_country": item.get("origin_country", []),
                "original_language": item.get("original_language"),
                "tmdb_url": f"https://www.themoviedb.org/tv/{item['id']}",
            }
            for item in results
        ]
