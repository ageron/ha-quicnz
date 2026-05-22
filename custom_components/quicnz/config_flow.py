"""Config flow for the Quic Broadband integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from quicnz import QuicAuthError, QuicClient, QuicError

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

from .const import CONF_SERVICE_ID, DOMAIN


class QuicNZConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Quic Broadband."""

    VERSION = 1

    def __init__(self) -> None:
        self._api_key: str | None = None
        self._service_ids: list[str] = []

    # ------------------------------------------------------------------
    # Initial setup – ask for the API key
    # ------------------------------------------------------------------

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the first step: collect and validate the API key."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key: str = user_input[CONF_API_KEY]
            try:
                async with QuicClient(api_key=api_key) as client:
                    service_ids = await client.get_services()
            except QuicAuthError:
                errors["base"] = "invalid_auth"
            except QuicError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                if not service_ids:
                    errors["base"] = "no_services"
                elif len(service_ids) == 1:
                    await self.async_set_unique_id(service_ids[0])
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=service_ids[0],
                        data={CONF_API_KEY: api_key, CONF_SERVICE_ID: service_ids[0]},
                    )
                else:
                    self._api_key = api_key
                    self._service_ids = service_ids
                    return await self.async_step_service()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Secondary step – choose a service when the account has several
    # ------------------------------------------------------------------

    async def async_step_service(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle service selection when multiple services exist."""
        if user_input is not None:
            service_id: str = user_input[CONF_SERVICE_ID]
            await self.async_set_unique_id(service_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=service_id,
                data={CONF_API_KEY: self._api_key, CONF_SERVICE_ID: service_id},
            )

        return self.async_show_form(
            step_id="service",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SERVICE_ID): SelectSelector(
                        SelectSelectorConfig(options=self._service_ids)
                    )
                }
            ),
        )

    # ------------------------------------------------------------------
    # Re-authentication – triggered when ConfigEntryAuthFailed is raised
    # ------------------------------------------------------------------

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Start reauthentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Collect a new API key during reauthentication."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key: str = user_input[CONF_API_KEY]
            try:
                async with QuicClient(api_key=api_key) as client:
                    await client.get_services()
            except QuicAuthError:
                errors["base"] = "invalid_auth"
            except QuicError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                reauth_entry = self._get_reauth_entry()
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data={**reauth_entry.data, CONF_API_KEY: api_key},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )
