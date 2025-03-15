# custom_components/smart_boiler/sensor.py
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    # Create the "Boiler State" sensor with a unique ID
    unique_id = f"{config_entry.entry_id}_boiler_state"
    boiler_state_sensor = SmartBoilerStateSensor(
        hass,
        config_entry,
        unique_id,
        config_entry.data["power_entity"],
        config_entry.data["power_threshold_standby"],
        config_entry.data["power_threshold_dhw"],
        config_entry.data["power_threshold_circulator"],
        config_entry.data["power_threshold_heating"],
    )

    # Add the main sensor to the list of entities
    async_add_entities([boiler_state_sensor], update_before_add=True)

    # Add a listener for real-time updates
    async_track_state_change(
        hass, config_entry.data["power_entity"], boiler_state_sensor.async_update_callback
    )

class SmartBoilerStateSensor(Entity):
    """Representation of the Smart Boiler State Sensor."""

    def __init__(self, hass, config_entry, unique_id, power_entity, threshold_standby, threshold_dhw, threshold_circulator, threshold_heating):
        """Initialize the sensor."""
        self._hass = hass
        self._config_entry = config_entry
        self._name = "Boiler State"
        self._unique_id = unique_id
        self._power_entity = power_entity
        self._threshold_standby = threshold_standby
        self._threshold_dhw = threshold_dhw
        self._threshold_circulator = threshold_circulator
        self._threshold_heating = threshold_heating
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor based on the current state."""
        if self._state == "heating":
            return "mdi:radiator"
        elif self._state == "dhw":
            return "mdi:water-pump"
        elif self._state == "standby":
            return "mdi:power-standby"
        elif self._state == "circulator":
            return "mdi:reload"
        elif self._state == "error":
            return "mdi:alert-circle"
        else:
            return "mdi:alert-circle"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return self._attributes

    async def async_update_callback(self, entity_id, old_state, new_state):
        """Handle state changes for the power sensor."""
        await self.async_update()
        self.async_write_ha_state()

    async def async_update(self):
        """Fetch new state data for the sensor."""
        power_state = self._hass.states.get(self._power_entity)
        if power_state is None or power_state.state in ["unknown", "unavailable"]:
            self._state = "error"
            return

        try:
            power = float(power_state.state)
        except (ValueError, TypeError):
            self._state = "error"
            return

        # Determine the boiler state
        if power < self._threshold_standby:
            self._state = "standby"
        elif self._threshold_standby <= power < self._threshold_dhw:
            self._state = "dhw"
        elif self._threshold_dhw <= power < self._threshold_circulator:
            self._state = "circulator"
        elif self._threshold_circulator <= power < self._threshold_heating:
            self._state = "heating"
        else:
            self._state = "error"

        # Update attributes
        self._attributes = {
            "power": power,
            "threshold_standby": self._threshold_standby,
            "threshold_dhw": self._threshold_dhw,
            "threshold_circulator": self._threshold_circulator,
            "threshold_heating": self._threshold_heating,
        }
