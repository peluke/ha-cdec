# Home Assistant CDEC

Home Assistant custom integration for CDEC stations and sensors. The default station is `MBG` (Briceburg), and the integration polls CDEC QueryF's current 15-minute data table.

This repository is packaged for HACS.

## Installation with HACS

This repository is not in the default HACS catalog. Add it as a custom repository:

1. Open **HACS** in Home Assistant.
2. Open **Integrations**.
3. Select the three-dot menu and choose **Custom repositories**.
4. Enter `https://github.com/peluke/ha-cdec`.
5. Select **Integration** as the category and click **Add**.
6. Search for **Home Assistant CDEC** and select **Download**.
7. Restart Home Assistant.
8. Go to **Settings > Devices & services > Add integration** and select **Home Assistant CDEC**.

The station ID defaults to `MBG`, but you can monitor any station hosted by CDEC. Find the station ID here: [CDEC station map](https://cdec-dev.water.ca.gov/webgis/?appid=cdecstation). After selecting a station, find its sensor number here: [CDEC sensor selector](https://cdec.water.ca.gov/dynamicapp/selectQuery). You need both the station ID and sensor number during setup.

The integration creates one Latest observation entity per configured CDEC sensor, defaulting to sensors `20`, `25`, and `4`. It discovers sensor types from CDEC, so other CDEC sensor numbers can be configured. The latest eight records for each sensor are available in the entity's `observations` attribute, with the full count in `observation_count`.

Polling frequency can be changed from the integration's Configure menu. The default is 15 minutes; valid values are 1 to 1440 minutes.

## Development

```text
python -m pytest tests
```

The integration has no API key and stores no secrets.
