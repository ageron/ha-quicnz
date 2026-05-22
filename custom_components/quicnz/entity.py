"""Base entity for the Quic Broadband integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import QuicNZCoordinator


class QuicNZEntity(CoordinatorEntity[QuicNZCoordinator]):
    """Base class for all Quic Broadband entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: QuicNZCoordinator, unique_id_suffix: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.service_id}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.service_id)},
            name=f"Quic {coordinator.service_id}",
            manufacturer="Quic Broadband",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://account.quic.nz/",
        )
