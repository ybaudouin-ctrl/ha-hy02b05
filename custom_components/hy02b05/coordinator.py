"""Coordinator."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.climate import HVACMode
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    HY02Preset,
    MANUFACTURER,
    MODEL,
)


@dataclass(slots=True)
class HY02State:

    available: bool = False

    power: bool = False

    current_temperature: float | None = None

    target_temperature: float | None = None

    hvac_mode: HVACMode = HVACMode.OFF

    preset_mode: str = HY02Preset.MANUAL

    child_lock: bool = False


class HY02Coordinator(DataUpdateCoordinator):

    def __init__(
        self,
        hass,
        topic: str,
    ):

        super().__init__(
            hass,
            logger=None,
            name=topic,
        )

        self.topic = topic

        self.state = HY02State()

        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, topic)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=topic,
        )