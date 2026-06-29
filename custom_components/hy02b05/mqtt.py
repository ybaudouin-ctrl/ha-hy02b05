"""MQTT support for HY02B05 thermostat integration."""

from __future__ import annotations

import json
import logging

from homeassistant.components import mqtt

from .coordinator import HY02Coordinator

_LOGGER = logging.getLogger(__name__)


class HY02MQTT:
    """Handle MQTT communication with HY02B05 device.

    Subscribes to Tasmota MQTT topics and updates coordinator state.
    """

    def __init__(self, coordinator: HY02Coordinator) -> None:
        """Initialize MQTT handler.

        Args:
            coordinator: HY02Coordinator instance
        """
        self.coordinator = coordinator
        self.hass = coordinator.hass
        self.topic = coordinator.topic

        self._unsubscribers: list = []

    async def async_subscribe(self) -> None:
        """Subscribe to all required MQTT topics."""
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

    async def async_unsubscribe(self) -> None:
        """Unsubscribe from all MQTT topics."""
        for unsub in self._unsubscribers:
            unsub()

        self._unsubscribers.clear()

    async def _sensor_message(self, msg) -> None:
        """Handle SENSOR telemetry message with temperature data.

        Args:
            msg: MQTT message object
        """
        try:
            payload = json.loads(msg.payload)
        except (json.JSONDecodeError, AttributeError) as err:
            _LOGGER.warning("Failed to parse SENSOR message: %s", err)
            return

        tuya = payload.get("TuyaSNS")

        if not tuya:
            return

        updated = False

        if "Temperature" in tuya:
            self.coordinator.state.current_temperature = tuya["Temperature"]
            updated = True

        if "TempSet" in tuya:
            self.coordinator.state.target_temperature = tuya["TempSet"]
            updated = True

        if updated:
            if not self.coordinator.state.available:
                self.coordinator.state.available = True
                _LOGGER.info("Device %s is now available", self.topic)
            self.coordinator.async_update_listeners()

    async def _power_message(self, msg) -> None:
        """Handle POWER status message.

        Args:
            msg: MQTT message object
        """
        try:
            payload = msg.payload
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")

            self.coordinator.state.power = payload.strip().upper() == "ON"

            if not self.coordinator.state.available:
                self.coordinator.state.available = True
                _LOGGER.info("Device %s is now available", self.topic)

            self.coordinator.async_update_listeners()
        except Exception as err:
            _LOGGER.error("Failed to process POWER message: %s", err)

    async def _result_message(self, msg) -> None:
        """Handle RESULT message with Tuya data point changes.

        Args:
            msg: MQTT message object
        """
        try:
            payload = json.loads(msg.payload)
        except (json.JSONDecodeError, AttributeError) as err:
            _LOGGER.warning("Failed to parse RESULT message: %s", err)
            return

        if "TuyaReceived" not in payload:
            return

        tuya = payload["TuyaReceived"]
        updated = False

        # DP4: Mode (Manual, Auto, Away, Override)
        if "DpType4Id4" in tuya:
            self.coordinator.state.preset_mode = str(tuya["DpType4Id4"])
            updated = True

        # DP6: Child Lock
        if "DpType1Id6" in tuya:
            self.coordinator.state.child_lock = tuya["DpType1Id6"] == 1
            updated = True

        if updated:
            if not self.coordinator.state.available:
                self.coordinator.state.available = True
                _LOGGER.info("Device %s is now available", self.topic)
            self.coordinator.async_update_listeners()

