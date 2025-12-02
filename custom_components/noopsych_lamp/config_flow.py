"""Config flow for Noopsych Lamp."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST

from .const import DOMAIN


class NoopsychLampConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Noopsych Lamp."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Здесь можно добавить проверку доступности хоста, если нужно
            # await self.hass.async_add_executor_job(test_connection, user_input[CONF_HOST])

            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )