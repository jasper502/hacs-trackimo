import aiohttp
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class TrackimoDataCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from the Trackimo API."""

    def __init__(self, hass: HomeAssistant, access_token: str):
        """Initialize the coordinator."""
        self.hass = hass
        self.access_token = access_token
        super().__init__(
            hass,
            _LOGGER,
            name="Trackimo Devices",
            update_interval=300,  # Update every 5 minutes
        )

    async def _async_update_data(self):
        """Fetch device data from the Trackimo API."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                async with session.get(
                    "https://app.trackimo.com/api/v3/accounts/%s/devices", headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Assume API returns a list of devices; adjust based on actual response
                        return {device["device_id"]: device for device in data}
                    else:
                        raise UpdateFailed(f"API error: {response.status}")
        except Exception as e:
            raise UpdateFailed(f"Error fetching data: {e}")

async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry, async_add_entities):
    """Set up the Trackimo integration from a config entry."""
    access_token = entry.data["token"]["access_token"]
    coordinator = TrackimoDataCoordinator(hass, access_token)
    await coordinator.async_config_entry_first_refresh()

    # Create device tracker entities
    from .device import TrackimoDevice  # Import here to avoid circular imports
    devices = coordinator.data
    entities = [TrackimoDevice(device_data, coordinator) for device_data in devices.values()]
    async_add_entities(entities)
