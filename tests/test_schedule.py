from datetime import UTC, datetime

import pytest

from custom_components.briceburg_cdec.schedule import (
    is_valid_scan_interval,
    poll_minutes_for_offset,
    should_poll_at,
)


def test_default_offset_runs_one_minute_after_each_quarter_hour():
    assert poll_minutes_for_offset(1) == (1, 16, 31, 46)


@pytest.mark.parametrize("minute", [1, 16, 31, 46])
def test_fifteen_minute_schedule_uses_each_slot(minute):
    assert should_poll_at(datetime(2026, 8, 26, 12, minute, tzinfo=UTC), 15, 1)


def test_thirty_minute_schedule_uses_alternating_slots():
    assert should_poll_at(datetime(2026, 8, 26, 12, 1, tzinfo=UTC), 30, 1)
    assert not should_poll_at(
        datetime(2026, 8, 26, 12, 16, tzinfo=UTC), 30, 1
    )
    assert should_poll_at(datetime(2026, 8, 26, 12, 31, tzinfo=UTC), 30, 1)


def test_forty_five_minute_schedule_stays_aligned_across_hours():
    assert should_poll_at(datetime(2026, 8, 26, 0, 1, tzinfo=UTC), 45, 1)
    assert should_poll_at(datetime(2026, 8, 26, 0, 46, tzinfo=UTC), 45, 1)
    assert should_poll_at(datetime(2026, 8, 26, 1, 31, tzinfo=UTC), 45, 1)
    assert not should_poll_at(
        datetime(2026, 8, 26, 1, 46, tzinfo=UTC), 45, 1
    )


def test_offset_must_be_within_a_quarter_hour():
    with pytest.raises(ValueError):
        poll_minutes_for_offset(15)


@pytest.mark.parametrize("interval", [15, 30, 45, 60, 1440])
def test_supported_intervals_are_multiples_of_fifteen(interval):
    assert is_valid_scan_interval(interval)


@pytest.mark.parametrize("interval", [1, 14, 16, 75, 1441])
def test_other_intervals_are_rejected(interval):
    assert not is_valid_scan_interval(interval)
