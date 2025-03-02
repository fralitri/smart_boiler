# custom_components/smart_boiler/sensor.py
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.const import UnitOfTemperature

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    entities = []

    # Aggiungi i sensori per le entità selezionate
    entities.append(SmartBoilerSensor("Hot Water Temperature", config_entry.data["hot_water_temp_entity"], UnitOfTemperature.CELSIUS))
    entities.append(SmartBoilerSensor("Cold Water Temperature", config_entry.data["cold_water_temp_entity"], UnitOfTemperature.CELSIUS))
    entities.append(SmartBoilerSensor("Heating Supply Temperature", config_entry.data["heating_supply_temp_entity"], UnitOfTemperature.CELSIUS))
    entities.append(SmartBoilerSensor("Heating Return Temperature", config_entry.data["heating_return_temp_entity"], UnitOfTemperature.CELSIUS))
    entities.append(SmartBoilerSensor("Flue Temperature", config_entry.data["flue_temp_entity"], UnitOfTemperature.CELSIUS))

    async_add_entities(entities)

class SmartBoilerSensor(Entity):
    """Representation of a Smart Boiler Sensor."""

    def __init__(self, name, entity_id, unit_of_measurement):
        """Initialize the sensor."""
        self._name = name
        self._entity_id = entity_id
        self._unit_of_measurement = unit_of_measurement
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    async def async_update(self):
        """Fetch new state data for the sensor."""
        state = self.hass.states.get(self._entity_id)
        if state:
            self._state = state.state