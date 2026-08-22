"""Constants for Home Assistant CDEC."""

DOMAIN = "ha_cdec"
NAME = "Home Assistant CDEC"
VERSION = "0.2.0"
DEFAULT_STATION = "MBG"
REPORT_URL = "https://cdec.water.ca.gov/dynamicapp/QueryF"
JSON_URL = "https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet"
CONF_STATION = "station"
CONF_SENSOR_NUM = "sensor_num"
DEFAULT_SENSOR_NUM = "20,25,4"
SENSOR_TYPES = {"4": "TEMP", "20": "FLOW", "25": "TEMP W"}
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL_MINUTES = 15
