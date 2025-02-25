from homeassistant.components.application_credentials import (
    AuthorizationServer,
    async_register_authorization_server,
)

async def async_setup(hass):
    await async_register_authorization_server(
        hass,
        "trackimo",
        AuthorizationServer(
            authorize_url="https://app.trackimo.com/api/v3/oauth2/auth",  # Replace with your actual authorization URL
            token_url="https://app.trackimo.com/api/v3/oauth2/token",          # Replace with your actual token URL
        ),
    )
