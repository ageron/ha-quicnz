"""Binary sensor platform for the Quic Broadband integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from quicnz.models import Session

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import QuicNZCoordinator
from .entity import QuicNZEntity


@dataclass(frozen=True, kw_only=True)
class QuicNZBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Extends BinarySensorEntityDescription with a value accessor."""

    value_fn: Callable[[Session], bool]


BINARY_SENSORS: tuple[QuicNZBinarySensorEntityDescription, ...] = (
    QuicNZBinarySensorEntityDescription(
        key="is_connected",
        translation_key="is_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda s: s.is_connected,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Quic Broadband binary sensors from a config entry."""
    coordinator: QuicNZCoordinator = entry.runtime_data
    async_add_entities(
        QuicNZBinarySensor(coordinator, desc) for desc in BINARY_SENSORS
    )


class QuicNZBinarySensor(QuicNZEntity, BinarySensorEntity):
    """A binary sensor entity for a single Quic Broadband boolean attribute."""

    entity_description: QuicNZBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: QuicNZCoordinator,
        description: QuicNZBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        """Return the binary sensor state from the latest coordinator data."""
        return self.entity_description.value_fn(self.coordinator.data)
