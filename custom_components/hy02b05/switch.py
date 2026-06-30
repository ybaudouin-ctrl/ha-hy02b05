"""Switch platform for HY02B05 thermostat integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import HY02Entity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch platform from config entry."""
    coordinator = hass.data["hy02b05"][entry.entry_id]

    async_add_entities([HY02ChildLockSwitch(coordinator)])


class HY02ChildLockSwitch(HY02Entity, SwitchEntity):
    """Child lock switch for the HY02B05 thermostat."""

    _attr_translation_key = "child_lock"
    _attr_unique_id_suffix = "child_lock"

    @property
    def is_on(self) -> bool:
        """Return true if child lock is enabled."""
        return self.coordinator.state.child_lock

    @property
    def icon(self) -> str:
        """Return the icon for the child lock state."""
        return "mdi:lock" if self.is_on else "mdi:lock-open-variant"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable child lock."""
        try:
            await self.coordinator.commands.set_child_lock(True)
            _LOGGER.debug("Enabled child lock for %s", self.coordinator.topic)
        except Exception as err:
            _LOGGER.error("Failed to enable child lock: %s", err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable child lock."""
        try:
            await self.coordinator.commands.set_child_lock(False)
            _LOGGER.debug("Disabled child lock for %s", self.coordinator.topic)
        except Exception as err:
            _LOGGER.error("Failed to disable child lock: %s", err)
