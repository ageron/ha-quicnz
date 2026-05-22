"""Image platform for the Quic Broadband integration."""

from __future__ import annotations

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from .const import DOMAIN
from .coordinator import QuicNZCoordinator, QuicNZWeathermapCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Quic Broadband weather map image entity."""
    coordinator: QuicNZCoordinator = entry.runtime_data
    async_add_entities([
        QuicNZWeathermapImage(coordinator.weathermap, coordinator.service_id)
    ])


class QuicNZWeathermapImage(
    CoordinatorEntity[QuicNZWeathermapCoordinator], ImageEntity
):
    """Image entity that displays the Quic network weather map."""

    _attr_content_type = "image/jpeg"
    _attr_has_entity_name = True
    _attr_translation_key = "weathermap"

    def __init__(
        self, coordinator: QuicNZWeathermapCoordinator, service_id: str
    ) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._attr_unique_id = f"{service_id}_weathermap"
        self._attr_image_last_updated = dt_util.utcnow()
        # Re-use the same device as the sensor/binary-sensor entities.
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, service_id)})

    async def async_image(self) -> bytes | None:
        """Return the latest weather map JPEG bytes."""
        return self.coordinator.data

    @callback
    def _handle_coordinator_update(self) -> None:
        """Bump image_last_updated so HA knows the image has changed."""
        self._attr_image_last_updated = dt_util.utcnow()
        super()._handle_coordinator_update()
