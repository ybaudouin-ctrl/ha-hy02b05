"""Climate platform for HY02B05."""

from __future__ import annotations

from homeassistant.components.climate import (
    ClimateEntity,
    HVACMode,
)

from homeassistant.components.climate.const import (
    ClimateEntityFeature,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import HY02Entity
from .const import HY02Mode

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):

    coordinator = hass.data["hy02b05"][entry.entry_id]

    async_add_entities(
        [
            HY02Climate(coordinator),
        ]
    )

class HY02Climate(HY02Entity, ClimateEntity):

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
def current_temperature(self):

    return self.coordinator.state.current_temperature


@property
def target_temperature(self):

    return self.coordinator.state.target_temperature

@property
def hvac_mode(self):

    if self.coordinator.state.power:

        return HVACMode.HEAT

    return HVACMode.OFF

@property
def preset_mode(self):

    mode = self.coordinator.state.mode

    if mode == HY02Mode.MANUAL:
        return "manual"

    if mode == HY02Mode.AUTO:
        return "auto"

    if mode == HY02Mode.AWAY:
        return "away"

    return "override"

async def async_set_temperature(self, **kwargs):

    temperature = kwargs.get("temperature")

    if temperature is None:
        return

    await self.coordinator.commands.set_temperature(
        temperature,
    )

async def async_set_hvac_mode(self, hvac_mode):

    if hvac_mode == HVACMode.OFF:

        await self.coordinator.commands.set_power(False)

    else:

        await self.coordinator.commands.set_power(True)

async def async_set_preset_mode(self, preset):

    if preset == "manual":

        await self.coordinator.commands.set_manual()

    elif preset == "auto":

        await self.coordinator.commands.set_auto()

    elif preset == "away":

        await self.coordinator.commands.set_away()

    elif preset == "override":

        await self.coordinator.commands.set_override()

