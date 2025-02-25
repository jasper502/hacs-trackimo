"""The Trackimo integration."""
import asyncio

import voluptuous as vol
import logging

from homeassistant import exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.device_tracker import DOMAIN as DEVICE_TRACKER

from trackimo import Trackimo

from .const import DOMAIN

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = [DEVICE_TRACKER]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Trackimo component."""
    return True


async def async_setup_entry(hass, entry):
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data["token"]["access_token"]
    await hass.config_entries.async_forward_entry_setups(entry, ["device_tracker"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
