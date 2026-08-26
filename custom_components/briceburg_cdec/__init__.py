"""Home Assistant CDEC integration."""

from __future__ import annotations

from .const import DOMAIN


async def async_reload_entry(hass, entry) -> None:
    """Reload Home Assistant CDEC after its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass, entry) -> bool:
    """Set up Home Assistant CDEC from a config entry."""
    from .coordinator import CdecCoordinator

    coordinator = CdecCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    coordinator.async_start_polling()
    entry.async_on_unload(coordinator.async_stop_polling)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass, entry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded
