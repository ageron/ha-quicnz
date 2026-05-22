"""DataUpdateCoordinator for the Quic Broadband integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from quicnz import QuicClient, QuicAuthError, QuicError
from quicnz.models import Session

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_SERVICE_ID, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class QuicNZCoordinator(DataUpdateCoordinator[Session]):
    """Fetch session data from the Quic API on a fixed schedule."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self._api_key: str = entry.data[CONF_API_KEY]
        self._service_id: str = entry.data[CONF_SERVICE_ID]

    @property
    def service_id(self) -> str:
        """Return the service ID being polled."""
        return self._service_id

    async def _async_update_data(self) -> Session:
        """Fetch the latest session data from the Quic API."""
        http_session = async_get_clientsession(self.hass)
        client = QuicClient(api_key=self._api_key, session=http_session)
        try:
            return await client.get_session(self._service_id)
        except QuicAuthError as err:
            raise ConfigEntryAuthFailed("Invalid or expired Quic API key") from err
        except QuicError as err:
            raise UpdateFailed(f"Error communicating with the Quic API: {err}") from err
