"""Sensor platform for the Quic Broadband integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from quicnz.models import Session

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import QuicNZCoordinator
from .entity import QuicNZEntity


@dataclass(frozen=True, kw_only=True)
class QuicNZSensorEntityDescription(SensorEntityDescription):
    """Extends SensorEntityDescription with a value accessor."""

    value_fn: Callable[[Session], str | int | float | datetime | None]


SENSORS: tuple[QuicNZSensorEntityDescription, ...] = (
    QuicNZSensorEntityDescription(
        key="status",
        translation_key="status",
        icon="mdi:check-network",
        value_fn=lambda s: s.status,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    QuicNZSensorEntityDescription(
        key="session_type",
        translation_key="session_type",
        icon="mdi:information-outline",
        value_fn=lambda s: s.session_type,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    QuicNZSensorEntityDescription(
        key="active_ipv4_prefix",
        translation_key="active_ipv4_prefix",
        icon="mdi:ip-network",
        value_fn=lambda s: s.active_ipv4_prefix,
    ),
    QuicNZSensorEntityDescription(
        key="active_ipv6_prefix",
        translation_key="active_ipv6_prefix",
        icon="mdi:ip-network-outline",
        value_fn=lambda s: s.active_ipv6_prefix,
    ),
    QuicNZSensorEntityDescription(
        key="last_radius_update",
        translation_key="last_radius_update",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda s: s.last_radius_update,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    QuicNZSensorEntityDescription(
        key="session_expires_at",
        translation_key="session_expires_at",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda s: s.session_expires_at,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    QuicNZSensorEntityDescription(
        key="lfc",
        translation_key="lfc",
        icon="mdi:office-building",
        value_fn=lambda s: s.service.lfc,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    QuicNZSensorEntityDescription(
        key="service_status",
        translation_key="service_status",
        icon="mdi:check-circle-outline",
        value_fn=lambda s: s.service.status,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    QuicNZSensorEntityDescription(
        key="datacap",
        translation_key="datacap",
        icon="mdi:database",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        state_class=SensorStateClass.MEASUREMENT,
        # datacap == 0 means uncapped; return None so the sensor shows unavailable
        value_fn=lambda s: s.service.datacap if s.service.datacap > 0 else None,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Quic Broadband sensors from a config entry."""
    coordinator: QuicNZCoordinator = entry.runtime_data
    async_add_entities(QuicNZSensor(coordinator, desc) for desc in SENSORS)


class QuicNZSensor(QuicNZEntity, SensorEntity):
    """A sensor entity for a single Quic Broadband session attribute."""

    entity_description: QuicNZSensorEntityDescription

    def __init__(
        self,
        coordinator: QuicNZCoordinator,
        description: QuicNZSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """Return the sensor value from the latest coordinator data."""
        return self.entity_description.value_fn(self.coordinator.data)
