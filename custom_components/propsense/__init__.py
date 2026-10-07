"""PropSense: rules from labels, floors, areas and groups.

Version 0.1 ships one action, exposing entities to voice assistants, driven
by rules you manage in the UI. The engine (``engine.py``) is pure policy and
actions are applied by ``manager.py``, so further actions can be added
without touching the rules model.
"""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.setup import async_setup_component

from .const import DOMAIN
from .manager import ExposureManager

PLATFORMS = [Platform.SENSOR]

type PropSenseConfigEntry = ConfigEntry[ExposureManager]

SERVICE_RESYNC = "resync"
SERVICE_PREVIEW = "preview"

_RESYNC_SCHEMA = vol.Schema({vol.Optional("dry_run", default=False): bool})


def _manager(hass: HomeAssistant) -> ExposureManager:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise ServiceValidationError("PropSense is not set up")
    return entries[0].runtime_data


async def async_setup_entry(hass: HomeAssistant, entry: PropSenseConfigEntry) -> bool:
    # Assistant exposure is stored by the core "homeassistant" integration.
    # It is always loaded in a running install, but do not depend on boot order.
    await async_setup_component(hass, "homeassistant", {})

    manager = ExposureManager(hass, entry)
    entry.runtime_data = manager

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await manager.async_start()

    if not hass.services.has_service(DOMAIN, SERVICE_RESYNC):

        async def _resync(call: ServiceCall) -> None:
            await _manager(hass).async_apply(dry_run=call.data["dry_run"])

        async def _preview(call: ServiceCall) -> ServiceResponse:
            result = await _manager(hass).async_apply(dry_run=True)
            return result.to_dict()

        hass.services.async_register(
            DOMAIN, SERVICE_RESYNC, _resync, schema=_RESYNC_SCHEMA
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_PREVIEW,
            _preview,
            supports_response=SupportsResponse.ONLY,
        )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PropSenseConfigEntry) -> bool:
    await entry.runtime_data.async_stop()
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded and not hass.config_entries.async_loaded_entries(DOMAIN):
        hass.services.async_remove(DOMAIN, SERVICE_RESYNC)
        hass.services.async_remove(DOMAIN, SERVICE_PREVIEW)
    return unloaded
