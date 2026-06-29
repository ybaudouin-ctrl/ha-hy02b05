"""Base entity for HY02B05 integration."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import HY02Coordinator


class HY02Entity(CoordinatorEntity[HY02Coordinator]):
    """Base entity for all HY02B05 entities.

    Provides common functionality:
    - Device info from coordinator
    - Availability tracking
    - Coordinator entity pattern with no polling
    - Entity naming via device and platform
    """

    _attr_has_entity_name = True
    _attr_should_poll = False

    @property
    def device_info(self):
        """Return device info from coordinator."""
        return self.coordinator.device_info

    @property
    def available(self) -> bool:
        """Return entity availability based on coordinator state."""
        return self.coordinator.state.available

    @property
    def unique_id(self) -> str:
        """Return unique ID for entity."""
        suffix = getattr(self, "_attr_unique_id_suffix", "unknown")
        return f"{self.coordinator.topic}_{suffix}"
