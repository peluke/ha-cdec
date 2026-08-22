import pytest

from custom_components.ha_cdec.json_parser import parse_json_data


def test_parse_json_data_normalizes_records():
    result = parse_json_data([
        {"sensorNum": 20, "date": "2026-08-20T18:45:00", "value": 1234, "units": "CFS"},
        {"sensorNum": 25, "date": "2026-08-20T19:00:00", "value": 1250, "units": "CFS"},
    ])
    assert result["latest"]["value"] == 1250
    assert result["latest"]["units"] == "CFS"
    assert len(result["observations"]) == 2
    assert result["by_sensor"]["20"][0]["value"] == 1234
    assert result["by_sensor"]["25"][0]["value"] == 1250


def test_parse_json_data_accepts_data_wrapper():
    result = parse_json_data({"data": [{"value": 1, "units": "CFS"}]})
    assert result["latest"]["value"] == 1


def test_parse_json_data_normalizes_cdec_field_casing_and_text_values():
    result = parse_json_data([{"SENSOR_NUM": 4, "VALUE": "12.5", "UNITS": "CFS"}])
    assert result["by_sensor"]["4"][0]["value"] == 12.5
    assert result["latest"]["units"] == "CFS"


def test_parse_json_data_rejects_empty_response():
    with pytest.raises(ValueError):
        parse_json_data([])
