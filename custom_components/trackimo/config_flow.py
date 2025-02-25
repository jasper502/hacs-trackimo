import requests
from homeassistant import config_entries
import voluptuous as vol

DOMAIN = "trackimo"

class TrackimoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required("username"): str,
                    vol.Required("password"): str,
                })
            )
        
        # Configuration from your example
        server_url = "https://app.trackimo.com"
        client_id = "554f7885-851c-4021-9c99-807b4034749e"
        client_secret = "fafda9c1ddf8ad673845a9e7269a753e"
        redirect_uri = "https://plus.trackimo.com/api/internal/v1/oauth_redirect"

        # Step 1: Login to get cookies
        try:
            resp = requests.post(
                f"{server_url}/api/internal/v2/user/login",
                headers={"Content-Type": "application/json"},
                json={"username": user_input["username"], "password": user_input["password"]}
            )
            resp.raise_for_status()
            cookies = dict(resp.cookies)
            if "JSESSIONID" not in cookies:
                raise Exception("Login failed: No JSESSIONID cookie received")
        
            # Step 2: Get authorization code
            auth_resp = requests.get(
                f"{server_url}/api/v3/oauth2/auth",
                params={
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                    "response_type": "code",
                    "scope": "locations,notifications,devices,accounts,settings,geozones"
                },
                cookies=cookies,
                allow_redirects=False
            )
            auth_resp.raise_for_status()
            location = auth_resp.headers["Location"]
            code = location.split("code=")[1]

            # Step 3: Exchange code for access token
            token_resp = requests.post(
                f"{server_url}/api/v3/oauth2/token",
                headers={"Content-Type": "application/json"},
                json={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code
                },
                cookies=cookies
            )
            token_resp.raise_for_status()
            access_token = token_resp.json().get("access_token")

            # Store the token in the config entry
            return self.async_create_entry(
                title="Trackimo",
                data={
                    "username": user_input["username"],
                    "access_token": access_token
                }
            )
        
        except Exception as e:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required("username"): str,
                    vol.Required("password"): str,
                }),
                errors={"base": str(e)}
            )
