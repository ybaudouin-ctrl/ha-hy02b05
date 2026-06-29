"""Constants for the HY02B05 integration."""

from __future__ import annotations

from enum import IntEnum, StrEnum

DOMAIN = "hy02b05"

MANUFACTURER = "Tuya"
MODEL = "HY02B05"

DEFAULT_NAME = "HY02B05 Thermostat"

#
# Tuya Data Points
#

DP_POWER = 1
DP_TARGET_TEMPERATURE = 2
DP_CURRENT_TEMPERATURE = 3
DP_MODE = 4
DP_CHILD_LOCK = 6


class HY02Mode(IntEnum):
    """HY02 operating modes."""

    MANUAL = 0
    AUTO = 1
    AWAY = 2
    OVERRIDE = 3


class HY02Preset(StrEnum):
    """Home Assistant preset names."""

    MANUAL = "manual"
    AUTO = "auto"
    AWAY = "away"
    OVERRIDE = "override"


PRESET_MODES = [
    HY02Preset.MANUAL,
    HY02Preset.AUTO,
    HY02Preset.AWAY,
    HY02Preset.OVERRIDE,
]
