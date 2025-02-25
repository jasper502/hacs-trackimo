from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import aiohttp
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "trackimo"

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Trackimo integration."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Trackimo from a config entry."""
    access_token = entry.data["access_token"]

    async def async_update_data():
        """Fetch data from the Trackimo API, refreshing the token if necessary."""
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {access_token}"}
            async with session.get("https://app.trackimo.com/api/v3/user", headers=headers) as resp:
                if resp.status == 401:  # Token expired
                    new_token = await refresh_access_token(hass, entry)
                    if new_token:
                        headers["Authorization"] = f"Bearer {new_token}"
                        async with session.get("https://app.trackimo.com/api/v3/user", headers=headers) as resp:
                            if resp.status != 200:
                                raise UpdateFailed(f"Failed to fetch data after token refresh: {resp.status}")
                            return await resp.json()
                    else:
                        raise UpdateFailed("Token refresh failed")
                elif resp.status != 200:
                    raise UpdateFailed(f"Failed to fetch data: {resp.status}")
                return await resp.json()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Trackimo",
        update_method=async_update_data,
        update_interval=asyncio.timedelta(minutes=5),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setup(entry, "device_tracker")
    return True

async def refresh_access_token(hass: HomeAssistant, entry: ConfigEntry) -> str | None:
    """Refresh the access token using the refresh token."""
    refresh_token = entry.data.get("refresh_token")
    if not refresh_token:
        _LOGGER.error("No refresh token available")
        return None

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://app.trackimo.com/api/v3/token",
            data={"refresh_token": refresh_token, "grant_type": "refresh_token"}
        ) as resp:
            if resp.status != 200:
                _LOGGER.error("Failed to refresh token: %s", resp.status)
                return None
            token_data = await resp.json()
            new_access_token = token_data.get("access_token")
            if new_access_token:
                hass.config_entries.async_update_entry(
                    entry, data={**entry.data, "access_token": new_access_token}
                )
                return new_access_token
            return None
