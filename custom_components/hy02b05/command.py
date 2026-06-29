"""MQTT commands for HY02B05."""

from __future__ import annotations

from homeassistant.components import mqtt

from .const import (
    MODE_AUTO,
    MODE_AWAY,
    MODE_MANUAL,
    MODE_OVERRIDE,
)


class HY02Commands:
    """Send commands to the thermostat."""

    def __init__(self, hass, topic: str):

        self.hass = hass
        self.topic = topic

    async def _publish(self, command: str, payload: str):

        await mqtt.async_publish(
            self.hass,
            f"cmnd/{self.topic}/{command}",
            payload,
            qos=1,
            retain=False,
        )

    #
    # -----------------------------------------------------------------
    # Power
    # -----------------------------------------------------------------
    #

    async def set_power(self, state: bool):

        value = 1 if state else 0

        await self._publish(
            "TuyaSend1",
            f"1,{value}",
        )

    #
    # -----------------------------------------------------------------
    # Temperature
    # -----------------------------------------------------------------
    #

    async def set_temperature(self, temperature: float):

        value = int(round(temperature * 10))

        await self._publish(
            "TuyaSend2",
            f"2,{value}",
        )

    #
    # -----------------------------------------------------------------
    # Child lock
    # -----------------------------------------------------------------
    #

    async def set_child_lock(self, state: bool):

        value = 1 if state else 0

        await self._publish(
            "TuyaSend1",
            f"6,{value}",
        )

    #
    # -----------------------------------------------------------------
    # Modes
    # -----------------------------------------------------------------
    #

    async def set_manual(self):

        await self._publish(
            "TuyaSend4",
            f"4,{MODE_MANUAL}",
        )

    async def set_auto(self):

        await self._publish(
            "TuyaSend4",
            f"4,{MODE_AUTO}",
        )

    async def set_away(self):

        await self._publish(
            "TuyaSend4",
            f"4,{MODE_AWAY}",
        )

    async def set_override(self):

        await self._publish(
            "TuyaSend4",
            f"4,{MODE_OVERRIDE}",
        )