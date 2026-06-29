"""Climate platform for HY02B05."""

from __future__ import annotations

from homeassistant.components.climate import (
    ClimateEntity,
    HVACMode,
)
from homeassistant.components.climate.const import ClimateEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import HY02Mode
from .entity import HY02Entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate platform."""
    coordinator = hass.data["hy02b05"][entry.entry_id]

    async_add_entities(
        [
            HY02Climate(coordinator),
        ]
    )


class HY02Climate(HY02Entity, ClimateEntity):
    """HY02B05 climate entity."""

    _attr_name = None

    _attr_temperature_unit = "°C"

    _attr_target_temperature_step = 0.5

    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
    )

    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.HEAT,
    ]

    _attr_preset_modes = [
        "manual",
        "auto",
        "away",
        "override",
    ]

    @property
    def current_temperature(self) -> float | None:
        """Return current temperature."""
        return self.coordinator.state.current_temperature

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature."""
        return self.coordinator.state.target_temperature

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        if self.coordinator.state.power:
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def preset_mode(self) -> str:
        """Return current preset mode."""
        mode_int = int(self.coordinator.state.preset_mode)

        if mode_int == HY02Mode.MANUAL:
            return "manual"
        if mode_int == HY02Mode.AUTO:
            return "auto"
        if mode_int == HY02Mode.AWAY:
            return "away"
        return "override"

    async def async_set_temperature(self, **kwargs) -> None:
        """Set target temperature."""
        temperature = kwargs.get("temperature")

        if temperature is None:
            return

        await self.coordinator.commands.set_temperature(temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.commands.set_power(False)
        else:
            await self.coordinator.commands.set_power(True)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode."""
        if preset_mode == "manual":
            await self.coordinator.commands.set_mode(HY02Mode.MANUAL)
        elif preset_mode == "auto":
            await self.coordinator.commands.set_mode(HY02Mode.AUTO)
        elif preset_mode == "away":
            await self.coordinator.commands.set_mode(HY02Mode.AWAY)
        elif preset_mode == "override":
            await self.coordinator.commands.set_mode(HY02Mode.OVERRIDE)
