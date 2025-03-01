# custom_components/smart_boiler/sensor.py
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    UnitOfTemperature,  # Celsius, Fahrenheit, ecc.
    UnitOfPressure,     # BAR, PASCAL, ecc.
    UnitOfVolume,       # CUBIC_METERS, LITERS, ecc.
    UnitOfPower,        # WATT, KILO_WATT, ecc.
)
from .const import DOMAIN, GAS_TYPES

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    entities = []

    # Aggiungi i sensori per le entità selezionate
    for key, entity_id in config_entry.data.items():
        if key.endswith("_entity"):
            entities.append(SmartBoilerSensor(key, entity_id))

    # Aggiungi i sensori per i parametri della caldaia
    gas_type = config_entry.data.get("gas_type")
    gas_flow_rate = config_entry.data.get("gas_flow_rate")
    calorific_value = GAS_TYPES[gas_type]["calorific_value"]

    # Calcola il consumo di gas
    gas_consumption_kwh = gas_flow_rate * calorific_value
    entities.append(SmartBoilerSensor("Gas Consumption", gas_consumption_kwh, UnitOfPower.KILO_WATT))

    async_add_entities(entities)

class SmartBoilerSensor(Entity):
    """Representation of a Smart Boiler Sensor."""

    def __init__(self, name, state, unit_of_measurement=None):
        """Initialize the sensor."""
        self._name = name
        self._state = state
        self._unit_of_measurement = unit_of_measurement

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
        # Qui puoi aggiungere la logica per aggiornare lo stato del sensore
        pass