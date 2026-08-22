"""Config flow for Briceburg CDEC."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .const import CONF_SCAN_INTERVAL, CONF_SENSOR_NUM, CONF_STATION, DEFAULT_SCAN_INTERVAL_MINUTES, DEFAULT_SENSOR_NUM, DEFAULT_STATION, DOMAIN, NAME


class BriceburgConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Briceburg CDEC config flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BriceburgOptionsFlow()

    async def async_step_user(self, user_input=None):
        """Handle the user step."""
        if user_input is not None:
            await self.async_set_unique_id(f"{DOMAIN}_{user_input[CONF_STATION].upper()}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_NAME], data=user_input
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=NAME): str,
                vol.Required(CONF_STATION, default=DEFAULT_STATION): str,
                vol.Required(CONF_SENSOR_NUM, default=DEFAULT_SENSOR_NUM): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)


class BriceburgOptionsFlow(config_entries.OptionsFlow):
    """Allow polling frequency changes without reinstalling the integration."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        interval = self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MINUTES)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {vol.Required(CONF_SCAN_INTERVAL, default=interval): vol.All(int, vol.Range(min=1, max=1440))}
            ),
        )
