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
    coordinator: EntertainmentCoordinator = entry.runtime_data
    async_add_entities(
        [
            EntertainmentSensor(coordinator, "theatrical", "Movies in Theaters", "mdi:movie-open"),
            EntertainmentSensor(coordinator, "digital", "Movies Released Digitally", "mdi:movie-open-outline"),
            EntertainmentSensor(coordinator, "tv", "TV Shows Airing", "mdi:television"),
        ]
    )


class EntertainmentSensor(CoordinatorEntity[EntertainmentCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator, data_key, name, icon):
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{DOMAIN}_{data_key}"

    @property
    def native_value(self) -> int:
        return len((self.coordinator.data or {}).get(self._data_key, []))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            "date": data.get("date"),
            "items": data.get(self._data_key, []),
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, "entertainment_releases")},
            name="Entertainment Releases",
            manufacturer="Community",
            model="TMDB Release Feed",
        )
