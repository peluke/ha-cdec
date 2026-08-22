from custom_components.briceburg_cdec.realtime_parser import parse_queryf


def test_parse_queryf_maps_current_sensor_types():
    html = """
    <h3>15 Minute Data</h3><table>
    <tr><th>DATE / TIME PDT</th><th>FLOW CFS</th><th>TEMP DEG F</th></tr>
    <tr><td>08/21/2026 15:00</td><td>57</td><td>74</td></tr>
    <tr><td>08/21/2026 15:15</td><td>--</td><td>--</td></tr></table>
    """
    result = parse_queryf(html, {"20": "FLOW", "4": "TEMP"})
    assert result["by_sensor"]["20"][-1]["value"] == 57
    assert result["by_sensor"]["4"][-1]["units"] == "DEG F"
