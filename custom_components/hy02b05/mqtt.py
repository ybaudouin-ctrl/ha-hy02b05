"""MQTT support for HY02B05."""

from __future__ import annotations

import json
import logging

from homeassistant.components import mqtt

from .coordinator import HY02Coordinator

_LOGGER = logging.getLogger(__name__)


class HY02MQTT:

    def __init__(self, coordinator: HY02Coordinator):

        self.coordinator = coordinator
        self.hass = coordinator.hass
        self.topic = coordinator.topic

        self._unsubscribers = []

    async def async_subscribe(self):

        self._unsubscribers.append(
            await mqtt.async_subscribe(
                self.hass,
                f"tele/{self.topic}/SENSOR",
                self._sensor_message,
                1,
            )
        )

        self._unsubscribers.append(
            await mqtt.async_subscribe(
                self.hass,
                f"tele/{self.topic}/RESULT",
                self._result_message,
                1,
            )
        )

        self._unsubscribers.append(
            await mqtt.async_subscribe(
                self.hass,
                f"stat/{self.topic}/POWER",
                self._power_message,
                1,
            )
        )

    async def async_unsubscribe(self):

        for unsub in self._unsubscribers:
            unsub()

        self._unsubscribers.clear()

    async def _sensor_message(self, msg):

        payload = json.loads(msg.payload)

        tuya = payload.get("TuyaSNS")

        if not tuya:
            return

        if "Temperature" in tuya:
            self.coordinator.state.current_temperature = tuya["Temperature"]

        if "TempSet" in tuya:
            self.coordinator.state.target_temperature = tuya["TempSet"]

        self.coordinator.async_update_listeners()

    async def _power_message(self, msg):

        payload = msg.payload
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")

        self.coordinator.state.power = payload.strip().upper() == "ON"

        self.coordinator.async_update_listeners()

    async def _result_message(self, msg):

        payload = json.loads(msg.payload)

        if "TuyaReceived" not in payload:
            return

        tuya = payload["TuyaReceived"]

        #
        # DP4
        #

        if "DpType4Id4" in tuya:

            self.coordinator.state.preset_mode = str(tuya["DpType4Id4"])

        #
        # DP6
        #

        if "DpType1Id6" in tuya:

            self.coordinator.state.child_lock = (
                tuya["DpType1Id6"] == 1
            )

        self.coordinator.async_update_listeners()
