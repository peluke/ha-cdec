"""Parse CDEC JSONDataServlet sensor metadata."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def _normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize CDEC field casing and common field aliases."""
    values = {str(key).lower(): value for key, value in record.items()}
    aliases = {
        "sensornum": "sensor_num",
        "sensornumber": "sensor_num",
        "sensor": "sensor_num",
        "sensortype": "sensor_type",
        "durcode": "dur_code",
        "stationid": "station_id",
        "obsdate": "obs_date",
        "measurementdate": "measurement_date",
    }
    normalized = {aliases.get(key, key): value for key, value in values.items()}
    value = normalized.get("value")
    if isinstance(value, str):
        try:
            normalized["value"] = float(value.strip())
        except ValueError:
            pass
    return normalized


def parse_json_data(payload: Any) -> dict[str, Any]:
    """Normalize CDEC records and select the newest observation."""
    if isinstance(payload, dict):
        records = payload.get("data", payload.get("records", []))
    else:
        records = payload
    if not isinstance(records, list) or not records:
        raise ValueError("CDEC response contained no observations")

    observations = [_normalize_record(record) for record in records if isinstance(record, dict)]
    if not observations:
        raise ValueError("CDEC response contained no observation objects")
    by_sensor: dict[str, list[dict[str, Any]]] = {}
    for record in observations:
        sensor = str(
            record.get("sensor_num", "unknown")
        )
        by_sensor.setdefault(sensor, []).append(record)
    latest = observations[-1]
    return {
        "latest": latest,
        "observations": observations,
        "by_sensor": by_sensor,
        "headers": sorted({key for record in observations for key in record}),
        "retrieved_at": datetime.now(UTC).isoformat(),
    }
