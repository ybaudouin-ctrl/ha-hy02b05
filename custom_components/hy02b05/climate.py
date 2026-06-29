"""Climate platform for HY02B05 thermostat integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    HVACMode,
)
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    PRESET_AWAY,
    PRESET_NONE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import HY02Mode
from .entity import HY02Entity

_LOGGER = logging.getLogger(__name__)

# Map HY02 preset modes to Home Assistant preset names
PRESET_MODE_MAP = {
    HY02Mode.MANUAL: PRESET_NONE,
    HY02Mode.AUTO: "auto",
    HY02Mode.AWAY: PRESET_AWAY,
    HY02Mode.OVERRIDE: "boost",
}

# Reverse mapping for setting modes
REVERSE_PRESET_MODE_MAP = {v: k for k, v in PRESET_MODE_MAP.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate platform from config entry."""
    coordinator = hass.data["hy02b05"][entry.entry_id]

    async_add_entities([HY02Climate(coordinator)])


class HY02Climate(HY02Entity, ClimateEntity):
    """HY02B05 thermostat climate entity.

    This entity represents the HY02B05 WiFi thermostat connected via MQTT.
    Supports:
    - HVAC mode: OFF/HEAT with Tasmota command routing
    - Current and target temperature from MQTT payloads
    - Preset modes: Manual, Auto, Away, Boost
    - Child lock state tracking
    - No polling; updates via MQTT subscription
    """

    _attr_name = None
    _attr_unique_id_suffix = "climate"

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5
    _attr_min_temp = 5.0
    _attr_max_temp = 35.0

    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )

    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.HEAT,
    ]

    _attr_preset_modes = [
        PRESET_NONE,  # manual
        "auto",
        PRESET_AWAY,
        "boost",
    ]

    @property
    def current_temperature(self) -> float | None:
        """Return current temperature from MQTT state."""
        temp = self.coordinator.state.current_temperature
        if temp is not None:
            return float(temp)
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature from MQTT state."""
        temp = self.coordinator.state.target_temperature
        if temp is not None:
            return float(temp)
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode based on power state."""
        if self.coordinator.state.power:
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        try:
            mode_int = int(self.coordinator.state.preset_mode)
            return PRESET_MODE_MAP.get(mode_int, PRESET_NONE)
        except (ValueError, TypeError):
            _LOGGER.warning(
                "Invalid preset_mode value: %s",
                self.coordinator.state.preset_mode,
            )
            return PRESET_NONE

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            "child_lock_enabled": self.coordinator.state.child_lock,
        }

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set target temperature via MQTT command.

        Args:
            temperature: Target temperature in °C
        """
        temperature = kwargs.get(ATTR_TEMPERATURE)

        if temperature is None:
            _LOGGER.error("Missing target temperature in set_temperature call")
            return

        try:
            await self.coordinator.commands.set_temperature(float(temperature))
            _LOGGER.debug("Set target temperature to %.1f°C", temperature)
        except Exception as err:
            _LOGGER.error("Failed to set temperature: %s", err)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode (power on/off) via MQTT command.

        Args:
            hvac_mode: HVACMode.HEAT to turn on, HVACMode.OFF to turn off
        """
        try:
            power_state = hvac_mode != HVACMode.OFF
            await self.coordinator.commands.set_power(power_state)
            _LOGGER.debug("Set HVAC mode to %s", hvac_mode)
        except Exception as err:
            _LOGGER.error("Failed to set HVAC mode: %s", err)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode via MQTT command.

        Args:
            preset_mode: One of: 'none', 'auto', 'away', 'boost'
        """
        try:
            mode_value = REVERSE_PRESET_MODE_MAP.get(preset_mode)
            if mode_value is None:
                _LOGGER.error(
                    "Invalid preset mode: %s. Valid modes: %s",
                    preset_mode,
                    list(REVERSE_PRESET_MODE_MAP.keys()),
                )
                return

            await self.coordinator.commands.set_mode(int(mode_value))
            _LOGGER.debug("Set preset mode to %s", preset_mode)
        except Exception as err:
            _LOGGER.error("Failed to set preset mode: %s", err)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on thermostat (set to HEAT mode)."""
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off thermostat (set to OFF mode)."""
        await self.async_set_hvac_mode(HVACMode.OFF)
