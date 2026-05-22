"""Image platform for the Quic Broadband integration."""

from __future__ import annotations

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
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


class QuicNZWeathermapImage(ImageEntity):
    """Image entity that displays the Quic network weather map."""

    _attr_content_type = "image/jpeg"
    _attr_has_entity_name = True
    _attr_translation_key = "weathermap"

    def __init__(
        self, coordinator: QuicNZWeathermapCoordinator, service_id: str
    ) -> None:
        # ImageEntity.__init__ must be called to set up access_tokens.
        super().__init__(coordinator.hass)
        self._coordinator = coordinator
        self._attr_unique_id = f"{service_id}_weathermap"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, service_id)})

    async def async_added_to_hass(self) -> None:
        """Subscribe to coordinator updates when the entity is added to HA."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self._coordinator.async_add_listener(self._handle_coordinator_update)
        )
        # The weathermap coordinator has no data yet on first setup; fetch now
        # so the image is available immediately rather than after 6 minutes.
        if self._coordinator.data is None:
            await self._coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Bump image_last_updated so HA knows the image has changed."""
        self._attr_image_last_updated = dt_util.utcnow()
        self.async_write_ha_state()

    async def async_image(self) -> bytes | None:
        """Return the latest weather map JPEG bytes."""
        return self._coordinator.data

    @property
    def available(self) -> bool:
        """Return True when the coordinator has successfully fetched data."""
        return self._coordinator.last_update_success
