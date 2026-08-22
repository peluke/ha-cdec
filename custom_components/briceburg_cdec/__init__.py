"""Briceburg CDEC integration."""

from __future__ import annotations

from .const import DOMAIN


async def async_setup_entry(hass, entry) -> bool:
    """Set up Briceburg CDEC from a config entry."""
    from .coordinator import BriceburgCoordinator

    coordinator = BriceburgCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass, entry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded
