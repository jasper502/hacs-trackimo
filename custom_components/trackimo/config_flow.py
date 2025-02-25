from homeassistant import config_entries
from homeassistant.helpers import config_entry_oauth2_flow

class TrackimoConfigFlow(config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain="trackimo"):
    """Handle the OAuth2 configuration flow for Trackimo."""

    DOMAIN = "trackimo"

    async def async_oauth_create_entry(self, data):
        """Create an entry after successful OAuth2 authentication."""
        return self.async_create_entry(title="Trackimo", data=data)
