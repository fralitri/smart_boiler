# custom_components/smart_boiler/sensor.py
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    UnitOfTemperature,  # Celsius, Fahrenheit, ecc.
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

    # Aggiungi il sensore per lo stato della caldaia
    entities.append(SmartBoilerStateSensor(
        config_entry.data.get("electric_consumption_entity"),
        config_entry.data.get("standby_power"),
        config_entry.data.get("hot_water_power"),
        config_entry.data.get("heating_power"),
    ))

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

class SmartBoilerStateSensor(Entity):
    """Representation of a Smart Boiler State Sensor."""

    def __init__(self, electric_consumption_entity, standby_power, hot_water_power, heating_power):
        """Initialize the sensor."""
        self._name = "Smart Boiler State"
        self._electric_consumption_entity = electric_consumption_entity
        self._standby_power = standby_power
        self._hot_water_power = hot_water_power
        self._heating_power = heating_power
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Fetch new state data for the sensor."""
        electric_consumption = self.hass.states.get(self._electric_consumption_entity).state
        standby_power = self._standby_power
        hot_water_power = self._hot_water_power
        heating_power = self._heating_power

        # Determina lo stato della caldaia in base al consumo elettrico
        if float(electric_consumption) <= standby_power:
            self._state = "Standby"
        elif standby_power < float(electric_consumption) <= hot_water_power:
            self._state = "Produzione Acqua Calda"
        else:
            self._state = "Riscaldamento"
