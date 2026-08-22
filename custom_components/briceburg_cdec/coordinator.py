"""CDEC JSON report retrieval."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any
from zoneinfo import ZoneInfo

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_SCAN_INTERVAL, CONF_SENSOR_NUM, CONF_STATION, DEFAULT_SCAN_INTERVAL_MINUTES, REPORT_URL, SENSOR_TYPES
from .realtime_parser import parse_queryf


class BriceburgCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Retrieve the CDEC JSON data report."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.station = entry.data[CONF_STATION].strip().upper()
        self.sensor_nums = [value.strip() for value in entry.data[CONF_SENSOR_NUM].split(",") if value.strip()]
        self.sensor_types = {number: SENSOR_TYPES[number] for number in self.sensor_nums if number in SENSOR_TYPES}
        interval_minutes = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MINUTES)
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=f"CDEC {self.station} sensors {','.join(self.sensor_nums)}",
            update_interval=timedelta(minutes=interval_minutes),
            always_update=True,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)
        today = datetime.now(ZoneInfo("America/Los_Angeles"))
        try:
            async with session.get(
                REPORT_URL,
                params={
                    "s": self.station,
                    "d": today.strftime("%d-%b-%Y %H:%M"),
                    "span": "25hours",
                },
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                response.raise_for_status()
                return parse_queryf(await response.text(), self.sensor_types)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            logging.getLogger(__name__).warning(
                "CDEC refresh failed for station %s sensors %s: %s",
                self.station,
                ",".join(self.sensor_nums),
                err,
            )
            raise UpdateFailed(f"Unable to read CDEC station {self.station}: {err}") from err
