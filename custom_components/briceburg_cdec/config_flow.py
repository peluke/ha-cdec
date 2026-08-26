"""Config flow for Home Assistant CDEC."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .const import (
    CONF_POLL_OFFSET,
    CONF_SCAN_INTERVAL,
    CONF_SENSOR_NUM,
    CONF_STATION,
    DEFAULT_POLL_OFFSET_MINUTES,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DEFAULT_SENSOR_NUM,
    DEFAULT_STATION,
    DOMAIN,
    NAME,
)
from .schedule import SUPPORTED_SCAN_INTERVALS, is_valid_scan_interval


def _valid_scan_interval(value: int) -> int:
    """Validate a clock-aligned polling interval."""
    value = int(value)
    if not is_valid_scan_interval(value):
        raise vol.Invalid("Select a supported clock-aligned polling interval")
    return value


class CdecConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the Home Assistant CDEC config flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return CdecOptionsFlow()

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


class CdecOptionsFlow(config_entries.OptionsFlow):
    """Allow CDEC settings to change without reinstalling the integration."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        interval = self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MINUTES)
        if not is_valid_scan_interval(int(interval)):
            interval = DEFAULT_SCAN_INTERVAL_MINUTES
        poll_offset = self.config_entry.options.get(
            CONF_POLL_OFFSET, DEFAULT_POLL_OFFSET_MINUTES
        )
        if not 0 <= int(poll_offset) <= 14:
            poll_offset = DEFAULT_POLL_OFFSET_MINUTES
        station = self.config_entry.options.get(CONF_STATION, self.config_entry.data[CONF_STATION])
        sensor_num = self.config_entry.options.get(CONF_SENSOR_NUM, self.config_entry.data[CONF_SENSOR_NUM])
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STATION, default=station): str,
                    vol.Required(CONF_SENSOR_NUM, default=sensor_num): str,
                    vol.Required(CONF_SCAN_INTERVAL, default=interval): vol.All(
                        vol.In(SUPPORTED_SCAN_INTERVALS), _valid_scan_interval
                    ),
                    vol.Required(CONF_POLL_OFFSET, default=poll_offset): vol.All(
                        int, vol.Range(min=0, max=14)
                    ),
                }
            ),
        )
