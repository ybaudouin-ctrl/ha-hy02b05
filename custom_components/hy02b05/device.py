from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HY02State:
    """Current thermostat state."""

    power: bool = False

    current_temperature: float | None = None

    target_temperature: float | None = None

    mode: int = 0

    child_lock: bool = False


class HY02Device:
    """Represents one thermostat."""

    def __init__(self, hass, topic: str):

        self.hass = hass

        self.topic = topic

        self.state = HY02State()

        self.listeners = []

    def add_listener(self, callback):

        self.listeners.append(callback)

    def notify(self):

        for callback in self.listeners:
            callback()