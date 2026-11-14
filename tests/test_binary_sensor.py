"""Tests for the HY02B05 physical heating status sensor."""

from types import SimpleNamespace

import pytest

from homeassistant.components.binary_sensor import BinarySensorDeviceClass

from custom_components.hy02b05.binary_sensor import HY02HeatingBinarySensor
from custom_components.hy02b05.mqtt import HY02MQTT


@pytest.mark.parametrize(
    ("payload", "expected"),
    [(b"ON", True), ("OFF", False), (b"on", True), (" off ", False)],
)
def test_heating_status_updates_independently(payload, expected):
    """POWER2 updates heating state without changing thermostat POWER1."""
    state = SimpleNamespace(available=False, power=True, heating_active=None)
    coordinator = SimpleNamespace(
        hass=SimpleNamespace(),
        topic="thermostat",
        state=state,
        async_update_listeners=lambda: None,
    )
    handler = HY02MQTT(coordinator)

    import asyncio

    asyncio.run(handler._async_heating_message(SimpleNamespace(payload=payload)))

    assert state.heating_active is expected
    assert state.power is True
    assert state.available is True


def test_heating_sensor_metadata():
    """The entity is presented as a heating binary sensor with a fire icon."""
    assert HY02HeatingBinarySensor._attr_device_class == BinarySensorDeviceClass.HEAT
    assert HY02HeatingBinarySensor._attr_icon == "mdi:fire"
