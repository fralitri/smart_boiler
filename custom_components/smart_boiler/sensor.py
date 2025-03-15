import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.core import callback
from homeassistant.helpers.translation import async_get_translations

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    # Load translations
    translations = await async_get_translations(hass, hass.config.language, "smart_boiler", "sensor")

    # Create the main boiler state sensor
    unique_id = f"{config_entry.entry_id}_boiler_state"
    boiler_state_sensor = SmartBoilerStateSensor(
        hass,
        translations["sensor.boiler_state.name"],  # Translated name
        unique_id,
        config_entry.data["power_entity"],
        config_entry.data["power_threshold_standby"],
        config_entry.data["power_threshold_acs"],
        config_entry.data["power_threshold_circulator"],
        config_entry.data["power_threshold_heating"],
    )

    # Add the main sensor to the list of entities
    async_add_entities([boiler_state_sensor], update_before_add=True)

    # Add a listener for real-time updates
    async_track_state_change(
        hass, config_entry.data["power_entity"], boiler_state_sensor.async_update_callback
    )

    # Create new sensors for ACS time, heating time, and total time
    unique_id_acs_time = f"{config_entry.entry_id}_acs_time"
    unique_id_heating_time = f"{config_entry.entry_id}_heating_time"
    unique_id_total_time = f"{config_entry.entry_id}_total_time"

    acs_time_sensor = SmartBoilerACSTimeSensor(
        hass,
        translations["sensor.acs_time.name"],  # Translated name
        unique_id_acs_time,
        config_entry.data["power_entity"],
        config_entry.data["power_threshold_acs"],
    )

    heating_time_sensor = SmartBoilerHeatingTimeSensor(
        hass,
        translations["sensor.heating_time.name"],  # Translated name
        unique_id_heating_time,
        config_entry.data["power_entity"],
        config_entry.data["power_threshold_heating"],
    )

    total_time_sensor = SmartBoilerTotalTimeSensor(
        hass,
        translations["sensor.total_time.name"],  # Translated name
        unique_id_total_time,
        unique_id_acs_time,
        unique_id_heating_time,
    )

    async_add_entities([acs_time_sensor, heating_time_sensor, total_time_sensor], update_before_add=True)

# Rest of the code remains unchanged...
