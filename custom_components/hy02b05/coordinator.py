"""Coordinator."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.climate import HVACMode
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    HY02Preset,
    MANUFACTURER,
    MODEL,
)

if TYPE_CHECKING:
    from .mqtt import HY02MQTT

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class HY02State:

    available: bool = False

    power: bool = False

    current_temperature: float | None = None

    target_temperature: float | None = None

    hvac_mode: HVACMode = HVACMode.OFF

    preset_mode: str = HY02Preset.MANUAL

    child_lock: bool = False


class HY02Commands:
    """Commands for HY02B05 via MQTT."""

    def __init__(self, coordinator: "HY02Coordinator") -> None:
        """Initialize commands."""
        self.coordinator = coordinator
        self.hass = coordinator.hass
        self.topic = coordinator.topic

    async def set_power(self, power: bool) -> None:
        """Set power state."""
        from homeassistant.components import mqtt

        payload = "ON" if power else "OFF"
        await mqtt.async_publish(
            self.hass,
            f"cmnd/{self.topic}/POWER",
            payload,
        )

    async def set_temperature(self, temperature: float) -> None:
        """Set target temperature."""
        from homeassistant.components import mqtt

        await mqtt.async_publish(
            self.hass,
            f"cmnd/{self.topic}/TuyaSend2",
            f"2,{int(temperature * 10)}",
        )

    async def set_mode(self, mode: int) -> None:
        """Set operating mode."""
        from homeassistant.components import mqtt

        await mqtt.async_publish(
            self.hass,
            f"cmnd/{self.topic}/TuyaSend1",
            f"4,{mode}",
        )

    async def set_child_lock(self, locked: bool) -> None:
        """Set child lock."""
        from homeassistant.components import mqtt

        payload = "1" if locked else "0"
        await mqtt.async_publish(
            self.hass,
            f"cmnd/{self.topic}/TuyaSend1",
            f"6,{payload}",
        )


class HY02Coordinator(DataUpdateCoordinator):
    """Coordinator for HY02B05 thermostat.

    Manages device state, MQTT communication, and command execution.
    """

    def __init__(
        self,
        hass,
        topic: str,
    ) -> None:
        """Initialize coordinator.

        Args:
            hass: Home Assistant instance
            topic: MQTT topic for the device
        """
        super().__init__(
            hass,
            logger=_LOGGER,
            name=topic,
        )

        self.topic = topic
        self.state = HY02State()
        self.commands = HY02Commands(self)

        from .mqtt import HY02MQTT

        self.mqtt: HY02MQTT = HY02MQTT(self)

        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, topic)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=topic,
        )

    async def _async_update_data(self) -> HY02State:
        """Fetch data from the coordinator.

        The coordinator is driven by MQTT messages, not polling.
        This method is required by DataUpdateCoordinator but does no actual polling.

        Returns:
            Current state
        """
        return self.state

    async def async_config_entry_first_refresh(self) -> None:
        """Establish MQTT connectivity on first refresh.

        Connects to MQTT topics before the first data refresh.
        """
        await self.mqtt.async_connect()
        await super().async_config_entry_first_refresh()

    async def async_shutdown(self) -> None:
        """Shut down the coordinator.

        Cleans up MQTT subscriptions and resources.
        """
        _LOGGER.debug("Shutting down coordinator for %s", self.topic)

        if self.mqtt and hasattr(self.mqtt, "async_disconnect"):
            try:
                await self.mqtt.async_disconnect()
            except Exception as err:
                _LOGGER.warning(
                    "Error disconnecting MQTT topics for %s: %s", self.topic, err
                )
