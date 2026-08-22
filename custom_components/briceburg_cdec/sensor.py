"""Sensors for Briceburg CDEC observations."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BriceburgCoordinator


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: BriceburgCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [CdecObservationSensor(coordinator, entry, sensor_num) for sensor_num in coordinator.sensor_nums]
    )


class _BaseSensor(CoordinatorEntity[BriceburgCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)}, name=entry.title, manufacturer="California Data Exchange Center"
        )

    @property
    def extra_state_attributes(self):
        return {"station": self.coordinator.station, "observations": self.coordinator.data["observations"]}


class CdecObservationSensor(_BaseSensor):
    """Expose the newest value returned for the configured CDEC sensor."""

    def __init__(self, coordinator, entry, sensor_num: str) -> None:
        super().__init__(coordinator, entry)
        self.sensor_num = sensor_num
        self._attr_name = f"Sensor {sensor_num} observation"
        self._attr_unique_id = f"{entry.entry_id}_sensor_{sensor_num}"

    @property
    def native_value(self):
        latest = self.coordinator.data["by_sensor"].get(self.sensor_num, [{}])[-1]
        return latest.get("value")

    @property
    def native_unit_of_measurement(self):
        latest = self.coordinator.data["by_sensor"].get(self.sensor_num, [{}])[-1]
        return latest.get("units")

    @property
    def extra_state_attributes(self):
        data = super().extra_state_attributes
        records = self.coordinator.data["by_sensor"].get(self.sensor_num, [])
        recent_records = records[-8:]
        data.update({
            "sensor_num": self.sensor_num,
            "latest": records[-1] if records else {},
            "observations": recent_records,
            "observation_count": len(records),
            "headers": self.coordinator.data["headers"],
            "retrieved_at": self.coordinator.data["retrieved_at"],
        })
        return data
