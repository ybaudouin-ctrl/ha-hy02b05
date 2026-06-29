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
    Implements proper HA 2025 MQTT lifecycle with sync callbacks.
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
        self._connected = False

    async def async_connect(self) -> None:
        """Connect to all required MQTT topics.

        Subscribes to device telemetry and status topics.
        Never subscribes twice; if already connected, does nothing.
        """
        if self._connected:
            _LOGGER.debug("MQTT handler already connected for %s", self.topic)
            return

        _LOGGER.debug("Connecting to MQTT for device %s", self.topic)

        try:
            # Subscribe to temperature and setpoint telemetry
            self._unsubscribers.append(
                await mqtt.async_subscribe(
                    self.hass,
                    f"tele/{self.topic}/SENSOR",
                    self._sensor_message,
                    1,
                )
            )
            _LOGGER.debug("Subscribed to tele/%s/SENSOR", self.topic)

            # Subscribe to Tuya result messages (mode, child lock, etc.)
            self._unsubscribers.append(
                await mqtt.async_subscribe(
                    self.hass,
                    f"tele/{self.topic}/RESULT",
                    self._result_message,
                    1,
                )
            )
            _LOGGER.debug("Subscribed to tele/%s/RESULT", self.topic)

            # Subscribe to power status
            self._unsubscribers.append(
                await mqtt.async_subscribe(
                    self.hass,
                    f"stat/{self.topic}/POWER",
                    self._power_message,
                    1,
                )
            )
            _LOGGER.debug("Subscribed to stat/%s/POWER", self.topic)

            self._connected = True
            _LOGGER.info("MQTT connected for device %s", self.topic)
        except Exception as err:
            _LOGGER.error("Failed to subscribe to MQTT topics: %s", err)
            self._unsubscribers.clear()
            raise

    async def async_disconnect(self) -> None:
        """Disconnect from all MQTT topics.

        Executes all unsubscribe callbacks and clears the list.
        """
        if not self._connected:
            _LOGGER.debug("MQTT handler not connected for %s", self.topic)
            return

        _LOGGER.debug("Disconnecting from MQTT for device %s", self.topic)

        for unsub in self._unsubscribers:
            try:
                unsub()
            except Exception as err:
                _LOGGER.warning("Error during MQTT unsubscribe: %s", err)

        self._unsubscribers.clear()
        self._connected = False
        _LOGGER.info("MQTT disconnected for device %s", self.topic)

    def _sensor_message(self, msg) -> None:
        """Handle SENSOR telemetry message with temperature data.

        This is a sync callback as required by HA MQTT API.
        Schedules async work via hass.create_task().

        Args:
            msg: MQTT message object
        """
        _LOGGER.debug(
            "Received SENSOR message on %s/SENSOR", self.topic
        )
        self.hass.create_task(self._async_sensor_message(msg))

    async def _async_sensor_message(self, msg) -> None:
        """Process SENSOR telemetry asynchronously.

        Args:
            msg: MQTT message object
        """
        try:
            payload = json.loads(msg.payload)
        except (json.JSONDecodeError, AttributeError, TypeError) as err:
            _LOGGER.warning(
                "Failed to parse SENSOR message for %s: %s", self.topic, err
            )
            return

        tuya = payload.get("TuyaSNS")
        if not tuya:
            return

        updated = False

        if "Temperature" in tuya:
            self.coordinator.state.current_temperature = tuya["Temperature"]
            _LOGGER.debug(
                "Updated current_temperature to %.1f for %s",
                tuya["Temperature"],
                self.topic,
            )
            updated = True

        if "TempSet" in tuya:
            self.coordinator.state.target_temperature = tuya["TempSet"]
            _LOGGER.debug(
                "Updated target_temperature to %.1f for %s",
                tuya["TempSet"],
                self.topic,
            )
            updated = True

        if updated:
            if not self.coordinator.state.available:
                self.coordinator.state.available = True
                _LOGGER.info("Device %s is now available", self.topic)
            self.coordinator.async_update_listeners()

    def _power_message(self, msg) -> None:
        """Handle POWER status message.

        This is a sync callback as required by HA MQTT API.
        Schedules async work via hass.create_task().

        Args:
            msg: MQTT message object
        """
        _LOGGER.debug("Received POWER message on %s/POWER", self.topic)
        self.hass.create_task(self._async_power_message(msg))

    async def _async_power_message(self, msg) -> None:
        """Process POWER status asynchronously.

        Args:
            msg: MQTT message object
        """
        try:
            payload = msg.payload
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")

            power = payload.strip().upper() == "ON"
            self.coordinator.state.power = power
            _LOGGER.debug("Updated power to %s for %s", power, self.topic)

            if not self.coordinator.state.available:
                self.coordinator.state.available = True
                _LOGGER.info("Device %s is now available", self.topic)

            self.coordinator.async_update_listeners()
        except Exception as err:
            _LOGGER.error(
                "Failed to process POWER message for %s: %s", self.topic, err
            )

    def _result_message(self, msg) -> None:
        """Handle RESULT message with Tuya data point changes.

        This is a sync callback as required by HA MQTT API.
        Schedules async work via hass.create_task().

        Args:
            msg: MQTT message object
        """
        _LOGGER.debug("Received RESULT message on %s/RESULT", self.topic)
        self.hass.create_task(self._async_result_message(msg))

    async def _async_result_message(self, msg) -> None:
        """Process RESULT message asynchronously.

        Args:
            msg: MQTT message object
        """
        try:
            payload = json.loads(msg.payload)
        except (json.JSONDecodeError, AttributeError, TypeError) as err:
            _LOGGER.warning(
                "Failed to parse RESULT message for %s: %s", self.topic, err
            )
            return

        if "TuyaReceived" not in payload:
            return

        tuya = payload["TuyaReceived"]
        updated = False

        # DP4: Mode (Manual, Auto, Away, Override)
        if "DpType4Id4" in tuya:
            self.coordinator.state.preset_mode = int(tuya["DpType4Id4"])
            _LOGGER.debug(
                "Updated preset_mode to %s for %s",
                tuya["DpType4Id4"],
                self.topic,
            )
            updated = True

        # DP6: Child Lock
        if "DpType1Id6" in tuya:
            self.coordinator.state.child_lock = tuya["DpType1Id6"] == 1
            _LOGGER.debug(
                "Updated child_lock to %s for %s",
                tuya["DpType1Id6"] == 1,
                self.topic,
            )
            updated = True

        if updated:
            if not self.coordinator.state.available:
                self.coordinator.state.available = True
                _LOGGER.info("Device %s is now available", self.topic)
            self.coordinator.async_update_listeners()
