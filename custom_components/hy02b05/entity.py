"""Base entity."""

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import HY02Coordinator


class HY02Entity(CoordinatorEntity[HY02Coordinator]):
    """Base entity."""

    _attr_has_entity_name = True

    _attr_should_poll = False

    @property
    def device_info(self):
        return self.coordinator.device_info

    @property
    def available(self):
        return self.coordinator.state.available