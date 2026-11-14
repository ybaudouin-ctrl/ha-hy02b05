"""Binary sensors for the HY02B05 thermostat."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import HY02Entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the heating status sensor from a config entry."""
    coordinator = hass.data["hy02b05"][entry.entry_id]
    async_add_entities([HY02HeatingBinarySensor(coordinator)])


class HY02HeatingBinarySensor(HY02Entity, BinarySensorEntity):
    """Report whether the thermostat's physical heating relay is active."""

    _attr_device_class = BinarySensorDeviceClass.HEAT
    _attr_icon = "mdi:fire"
    _attr_name = None
    _attr_translation_key = "heating"
    _attr_unique_id_suffix = "heating"

    @property
    def is_on(self) -> bool | None:
        """Return POWER2 state; None means no status has been received yet."""
        return self.coordinator.state.heating_active
