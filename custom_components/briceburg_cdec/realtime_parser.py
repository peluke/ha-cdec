"""Parser for the current 15-minute CDEC QueryF table."""

from __future__ import annotations

from datetime import datetime
from html.parser import HTMLParser
import re
from typing import Any


class _QueryFParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self.heading = ""
        self.in_heading = False
        self.in_target_table = False
        self.in_row = False
        self.in_cell = False
        self.cell: list[str] = []
        self.row: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "h3":
            self.in_heading = True
            self.heading = ""
        elif tag == "table":
            self.in_target_table = "15 minute" in self.heading.lower()
        elif tag == "tr" and self.in_target_table:
            self.in_row = True
            self.row = []
        elif tag in ("th", "td") and self.in_row:
            self.in_cell = True
            self.cell = []

    def handle_data(self, data: str) -> None:
        if self.in_heading:
            self.heading += data
        if self.in_cell:
            self.cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h3":
            self.in_heading = False
        elif tag in ("th", "td") and self.in_cell:
            value = " ".join("".join(self.cell).split())
            if value:
                self.row.append(value)
            self.in_cell = False
        elif tag == "tr" and self.in_target_table:
            if self.row:
                self.rows.append(self.row)
            self.in_row = False
        elif tag == "table":
            self.in_target_table = False


def _number(value: str) -> float | int | str:
    try:
        result = float(value.replace(",", "").strip())
    except ValueError:
        return value
    return int(result) if result.is_integer() else result


def _is_missing(value: str) -> bool:
    """Return whether QueryF marks a value as unavailable."""
    return value.strip().upper() in {"", "--", "-", "N/A", "NA", "-9999"}


def _sensor_type(header: str) -> tuple[str, str] | None:
    match = re.match(r"(.+?)\s+((?:DEG F|CFS|FEET|INCHES|MPH|DEG|%))$", header)
    if not match:
        return None
    return match.group(1).strip().upper(), match.group(2).strip()


def parse_queryf(html: str, sensor_types: dict[str, str]) -> dict[str, Any]:
    """Parse QueryF's 15-minute table into the coordinator data shape."""
    parser = _QueryFParser()
    parser.feed(html)
    if len(parser.rows) < 2:
        raise ValueError("CDEC QueryF response contained no 15-minute table")

    headers = [_sensor_type(header) for header in parser.rows[0][1:]]
    observations: list[dict[str, Any]] = []
    for row in parser.rows[1:]:
        if len(row) < 2:
            continue
        timestamp = row[0]
        for index, sensor_value in enumerate(row[1:]):
            if index >= len(headers) or headers[index] is None:
                continue
            if _is_missing(sensor_value):
                continue
            sensor_type, units = headers[index]
            sensor_num = next((number for number, kind in sensor_types.items() if kind == sensor_type), None)
            if sensor_num is None:
                continue
            observations.append({
                "station_id": "MBG",
                "sensor_num": sensor_num,
                "sensor_type": sensor_type,
                "date": timestamp,
                "value": _number(sensor_value),
                "units": units,
            })
    if not observations:
        raise ValueError("CDEC QueryF response contained no configured sensor data")

    by_sensor: dict[str, list[dict[str, Any]]] = {}
    for record in observations:
        by_sensor.setdefault(record["sensor_num"], []).append(record)
    return {
        "latest": observations[-1],
        "observations": observations,
        "by_sensor": by_sensor,
        "headers": sorted({key for record in observations for key in record}),
        "retrieved_at": datetime.now().isoformat(),
    }
