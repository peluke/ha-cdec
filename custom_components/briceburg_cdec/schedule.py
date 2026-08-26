"""Wall-clock polling schedule helpers for Home Assistant CDEC."""

from __future__ import annotations

from datetime import datetime

MIN_SCAN_INTERVAL_MINUTES = 15
MAX_SCAN_INTERVAL_MINUTES = 1440
SUPPORTED_SCAN_INTERVALS = (
    15,
    30,
    45,
    60,
    90,
    120,
    180,
    240,
    360,
    480,
    720,
    1440,
)


def poll_minutes_for_offset(offset_minutes: int) -> tuple[int, ...]:
    """Return the four minute marks for a quarter-hour polling offset."""
    if not 0 <= offset_minutes < MIN_SCAN_INTERVAL_MINUTES:
        raise ValueError("Polling offset must be from 0 through 14 minutes")
    return tuple(range(offset_minutes, 60, MIN_SCAN_INTERVAL_MINUTES))


def is_valid_scan_interval(interval_minutes: int) -> bool:
    """Return whether an interval can use quarter-hour wall-clock slots."""
    return interval_minutes in SUPPORTED_SCAN_INTERVALS


def should_poll_at(
    now: datetime, interval_minutes: int, offset_minutes: int
) -> bool:
    """Return whether a scheduled quarter-hour callback is a polling slot."""
    if not is_valid_scan_interval(interval_minutes):
        raise ValueError("Polling interval must be a multiple of 15 minutes")
    poll_minutes_for_offset(offset_minutes)
    minutes_since_midnight = now.hour * 60 + now.minute
    return (minutes_since_midnight - offset_minutes) % interval_minutes == 0
