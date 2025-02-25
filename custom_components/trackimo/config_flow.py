"""Config flow for Trackimo integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries, core, exceptions

from homeassistant.helpers import config_entry_oauth2_flow

from homeassistant.components.application_credentials import (
    AuthorizationServer,
    async_register_authorization_server,
)

from trackimo import Trackimo

from .const import DOMAIN, TRACKIMO_CLIENTID, TRACKIMO_CLIENTSECRET

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({"username": str, "password": str})

async def async_setup(hass):
    await async_register_authorization_server(
        hass,
        "trackimo",
        AuthorizationServer(
            authorize_url="https://app.trackimo.com/api/v3/oauth2/auth",  # Verify URL
            token_url="https://api.trackimo.com/api/v3/oauth2/token",          # Verify URL
        ),
    )

async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    api = Trackimo(
        loop=hass.loop, client_id=TRACKIMO_CLIENTID, client_secret=TRACKIMO_CLIENTSECRET
    )

    if not await api.login(data["username"], data["password"]):
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    auth_data = api.auth
    title = api.account.name if api.account.name else "Trackimo Device Tracker"

    # Return info that you want to store in the config entry.
    return {
        "title": title,
        "token": auth_data["token"],
        "refresh": auth_data["refresh"],
        "expires": auth_data["expires"],
        "username": data["username"],
        "password": data["password"],
        "clientid": TRACKIMO_CLIENTID,
        "clientsecret": TRACKIMO_CLIENTSECRET,
    }


_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entry_oauth2_flow.AbstractOAuth2FlowHandler):
    DOMAIN = "trackimo"

    async def async_oauth_create_entry(self, data):
        return self.async_create_entry(title="Trackimo", data=data)



#class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
#    """Handle a config flow for Trackimo."""
#
#   VERSION = 1
#    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
#
#    async def async_step_user(self, user_input=None):
#        """Handle the initial step."""
#        errors = {}
#        if user_input is not None:
#            try:
#                info = await validate_input(self.hass, user_input)
#
#                if "expires" in info:
#                    info["expires"] = info["expires"].timestamp()
#
#                return self.async_create_entry(title=info["title"], data=info)
#            except CannotConnect:
#                errors["base"] = "cannot_connect"
#            except InvalidAuth:
#                errors["base"] = "invalid_auth"
#            except Exception:  # pylint: disable=broad-except
#                _LOGGER.exception("Unexpected exception")
#                errors["base"] = "unknown"
#
#        return self.async_show_form(
#            step_id="user", data_schema=DATA_SCHEMA, errors=errors
#        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
