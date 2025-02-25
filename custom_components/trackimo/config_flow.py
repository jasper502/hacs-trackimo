import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from .const import DOMAIN, CONF_CLIENT_ID, CONF_CLIENT_SECRET

class TrackimoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle Trackimo configuration."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step where user inputs credentials."""
        if user_input is None:
            schema = vol.Schema({
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_CLIENT_ID): str,
                vol.Required(CONF_CLIENT_SECRET): str,
            })
            return self.async_show_form(step_id="user", data_schema=schema)

        # Perform the authentication steps
        async with aiohttp.ClientSession() as session:
            # Step 1: Login to get cookies
            login_url = "https://app.trackimo.com/api/internal/v2/user/login"
            login_data = {
                "username": user_input[CONF_USERNAME],
                "password": user_input[CONF_PASSWORD]
            }
            async with session.post(login_url, json=login_data) as resp:
                if resp.status != 200:
                    return self.async_show_form(step_id="user", errors={"base": "login_failed"})
                cookies = session.cookie_jar.filter_cookies(login_url)

            # Step 2: Get authorization code
            auth_url = "https://app.trackimo.com/api/v3/oauth2/auth"
            params = {
                "client_id": user_input[CONF_CLIENT_ID],
                "redirect_uri": "https://plus.trackimo.com/api/internal/v1/oauth_redirect",
                "response_type": "code",
                "scope": "locations,notifications,devices,accounts,settings,geozones",
            }
            async with session.get(auth_url, params=params, cookies=cookies, allow_redirects=False) as resp:
                if resp.status != 302:
                    return self.async_show_form(step_id="user", errors={"base": "auth_failed"})
                location = resp.headers["Location"]
                code = location.split("code=")[1]

            # Step 3: Exchange code for access token
            token_url = "https://app.trackimo.com/api/v3/oauth2/token"
            token_data = {
                "client_id": user_input[CONF_CLIENT_ID],
                "client_secret": user_input[CONF_CLIENT_SECRET],
                "code": code,
            }
            async with session.post(token_url, json=token_data, cookies=cookies) as resp:
                if resp.status != 200:
                    return self.async_show_form(step_id="user", errors={"base": "token_failed"})
                token_resp = await resp.json()
                access_token = token_resp.get("access_token")

        # Create the config entry with the access token
        return self.async_create_entry(
            title="Trackimo",
            data={
                "username": user_input[CONF_USERNAME],
                "access_token": access_token,
            }
        )
