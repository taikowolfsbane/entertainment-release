from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EntertainmentCoordinator


async def async_setup_entry(
    hass,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create Entertainment Releases sensors."""
    coordinator: EntertainmentCoordinator = entry.runtime_data

    async_add_entities(
        [
            EntertainmentSensor(
                coordinator,
                "theatrical",
                "Movies in Theaters",
                "mdi:movie-open",
                "theatrical_days",
            ),
            EntertainmentSensor(
                coordinator,
                "digital",
                "Movies Released Digitally",
                "mdi:movie-open-outline",
                "digital_days",
            ),
            EntertainmentSensor(
                coordinator,
                "tv",
                "TV Shows Airing",
                "mdi:television",
                "tv_days",
            ),
        ]
    )


class EntertainmentSensor(
    CoordinatorEntity[EntertainmentCoordinator],
    SensorEntity,
):
    """Represent one entertainment release category."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: EntertainmentCoordinator,
        data_key: str,
        name: str,
        icon: str,
        days_key: str,
    ) -> None:
        """Initialize a release sensor."""
        super().__init__(coordinator)

        self._data_key = data_key
        self._days_key = days_key
        self._attr_name = name
        self._attr_icon = icon

        # Keep v0.1.0 unique IDs so upgrades retain existing entities.
        self._attr_unique_id = f"{DOMAIN}_{data_key}"

    @property
    def native_value(self) -> int:
        """Return the number of matching releases."""
        return len(
            (self.coordinator.data or {}).get(
                self._data_key,
                [],
            )
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return release data and configured window."""
        data = self.coordinator.data or {}

        return {
            "date": data.get("date"),
            "region": data.get("region"),
            "lookahead_days": data.get(self._days_key),
            "items": data.get(self._data_key, []),
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return the shared integration device."""
        return DeviceInfo(
            identifiers={(DOMAIN, "entertainment_releases")},
            name="Entertainment Releases",
            manufacturer="Community",
            model="TMDB Release Feed",
        )
