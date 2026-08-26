"""Retrieve current CDEC observations and sensor metadata."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_POLL_OFFSET,
    CONF_SCAN_INTERVAL,
    CONF_SENSOR_NUM,
    CONF_STATION,
    DEFAULT_POLL_OFFSET_MINUTES,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    JSON_URL,
    REPORT_URL,
    SENSOR_TYPES,
)
from .json_parser import parse_json_data
from .realtime_parser import parse_queryf
from .schedule import is_valid_scan_interval, poll_minutes_for_offset, should_poll_at


class CdecCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate current CDEC observations."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.station = entry.options.get(CONF_STATION, entry.data[CONF_STATION]).strip().upper()
        sensor_config = entry.options.get(CONF_SENSOR_NUM, entry.data[CONF_SENSOR_NUM])
        self.sensor_nums = [value.strip() for value in sensor_config.split(",") if value.strip()]
        self.sensor_types = {number: SENSOR_TYPES[number] for number in self.sensor_nums if number in SENSOR_TYPES}
        interval_minutes = int(
            entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MINUTES)
        )
        if not is_valid_scan_interval(interval_minutes):
            logging.getLogger(__name__).warning(
                "Invalid CDEC polling interval %s; using %s minutes",
                interval_minutes,
                DEFAULT_SCAN_INTERVAL_MINUTES,
            )
            interval_minutes = DEFAULT_SCAN_INTERVAL_MINUTES
        offset_minutes = int(
            entry.options.get(CONF_POLL_OFFSET, DEFAULT_POLL_OFFSET_MINUTES)
        )
        try:
            self.poll_minutes = poll_minutes_for_offset(offset_minutes)
        except ValueError:
            logging.getLogger(__name__).warning(
                "Invalid CDEC polling offset %s; using %s minute",
                offset_minutes,
                DEFAULT_POLL_OFFSET_MINUTES,
            )
            offset_minutes = DEFAULT_POLL_OFFSET_MINUTES
            self.poll_minutes = poll_minutes_for_offset(offset_minutes)
        self.scan_interval_minutes = interval_minutes
        self.poll_offset_minutes = offset_minutes
        self._unsub_polling: Callable[[], None] | None = None
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=f"CDEC {self.station} sensors {','.join(self.sensor_nums)}",
            update_interval=None,
            always_update=True,
        )

    @callback
    def async_start_polling(self) -> None:
        """Start the clock-aligned CDEC polling schedule."""
        if self._unsub_polling is not None:
            return
        self._unsub_polling = async_track_time_change(
            self.hass,
            self._handle_scheduled_refresh,
            minute=list(self.poll_minutes),
            second=0,
        )

    @callback
    def async_stop_polling(self) -> None:
        """Stop the clock-aligned CDEC polling schedule."""
        if self._unsub_polling is not None:
            self._unsub_polling()
            self._unsub_polling = None

    async def _handle_scheduled_refresh(self, now: datetime) -> None:
        """Request a refresh when the current wall-clock slot is enabled."""
        if should_poll_at(
            now, self.scan_interval_minutes, self.poll_offset_minutes
        ):
            await self.async_request_refresh()

    async def _async_update_data(self) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)
        today = datetime.now(ZoneInfo("America/Los_Angeles"))
        try:
            async with session.get(
                JSON_URL,
                params={
                    "Stations": self.station,
                    "SensorNums": ",".join(self.sensor_nums),
                    "dur_code": "E",
                    "Start": "",
                    "End": today.strftime("%Y-%m-%dT%H:%M"),
                },
                timeout=aiohttp.ClientTimeout(total=30),
            ) as metadata_response:
                metadata_response.raise_for_status()
                metadata = parse_json_data(await metadata_response.json(content_type=None))
                for record in metadata["observations"]:
                    sensor_num = str(record.get("sensor_num", ""))
                    sensor_type = record.get("sensor_type")
                    if sensor_num and sensor_type:
                        self.sensor_types[sensor_num] = str(sensor_type).upper()
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
                return parse_queryf(await response.text(), self.sensor_types, self.station)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            logging.getLogger(__name__).warning(
                "CDEC refresh failed for station %s sensors %s: %s",
                self.station,
                ",".join(self.sensor_nums),
                err,
            )
            raise UpdateFailed(f"Unable to read CDEC station {self.station}: {err}") from err
