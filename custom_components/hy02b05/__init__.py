"""HY02B05 integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PLATFORMS = ("climate","sensor","switch","select")


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HY02B05 from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload HY02B05."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
