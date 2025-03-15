"""The Smart Boiler integration."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "smart_boiler"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Smart Boiler component."""
    return True

async def async_setup_entry(hass: HomeAssistant, config_entry):
    """Set up Smart Boiler from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, config_entry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
    return True
