from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.helpers.entity import DeviceInfo

class TrackimoDevice(TrackerEntity):
    """Representation of a Trackimo device tracker."""

    def __init__(self, device_data, coordinator):
        """Initialize the device tracker."""
        self._device_data = device_data
        self._coordinator = coordinator
        self._unique_id = device_data["device_id"]
        self._name = device_data["name"]

    @property
    def unique_id(self):
        """Return the unique ID of the device."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def latitude(self):
        """Return the latitude of the device."""
        return self._device_data["latitude"]

    @property
    def longitude(self):
        """Return the longitude of the device."""
        return self._device_data["longitude"]

    @property
    def location_accuracy(self):
        """Return the location accuracy in meters."""
        return self._device_data.get("accuracy", 0)

    @property
    def device_info(self):
        """Return device information for the device registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            name=self._name,
            manufacturer="Trackimo",
        )

    async def async_update(self):
        """Update the entity with the latest data."""
        await self._coordinator.async_request_refresh()
        self._device_data = self._coordinator.data.get(self._unique_id, self._device_data)

DOMAIN = "trackimo"
