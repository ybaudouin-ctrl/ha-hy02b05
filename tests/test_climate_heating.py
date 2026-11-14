"""Tests for physical heating presentation on the climate entity."""

from types import SimpleNamespace

import pytest

from homeassistant.components.climate import HVACAction

from custom_components.hy02b05.climate import HY02Climate


@pytest.mark.parametrize(
    ("power", "heating_active", "expected_action", "expected_icon"),
    [
        (False, True, HVACAction.OFF, "mdi:fire"),
        (True, None, None, "mdi:thermostat"),
        (True, False, HVACAction.IDLE, "mdi:thermostat"),
        (True, True, HVACAction.HEATING, "mdi:fire"),
    ],
)
def test_climate_presents_physical_heating(
    power, heating_active, expected_action, expected_icon
):
    """The action and flame icon reflect POWER2, independently from mode."""
    climate = HY02Climate.__new__(HY02Climate)
    climate.coordinator = SimpleNamespace(
        state=SimpleNamespace(power=power, heating_active=heating_active)
    )

    assert climate.hvac_action == expected_action
    assert climate.icon == expected_icon
