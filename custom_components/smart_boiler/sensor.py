# custom_components/smart_boiler/sensor.py
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.const import UnitOfTemperature

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler integration."""
    # Non creiamo nuovi sensori, ma utilizziamo quelli esistenti.
    # Possiamo invece creare un'entità virtuale per raggruppare i dati.
    entities = []

    # Creiamo un'entità virtuale per raggruppare i dati
    entities.append(SmartBoilerGroupSensor("Smart Boiler Status", config_entry.data))

    async_add_entities(entities)

class SmartBoilerGroupSensor(Entity):
    """Representation of a Smart Boiler Group Sensor."""

    def __init__(self, name, config_data):
        """Initialize the sensor."""
        self._name = name
        self._config_data = config_data
        self._state = "ok"  # Stato predefinito
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return self._attributes

    async def async_update(self):
        """Fetch new state data for the sensor."""
        # Aggiorna gli attributi con i valori delle entità esistenti
        self._attributes = {
            "hot_water_temperature": self.hass.states.get(self._config_data["hot_water_temp_entity"]).state,
            "cold_water_temperature": self.hass.states.get(self._config_data["cold_water_temp_entity"]).state,
            "heating_supply_temperature": self.hass.states.get(self._config_data["heating_supply_temp_entity"]).state,
            "heating_return_temperature": self.hass.states.get(self._config_data["heating_return_temp_entity"]).state,
            "flue_temperature": self.hass.states.get(self._config_data["flue_temp_entity"]).state,
        }

        # Puoi aggiungere logica per calcolare lo stato complessivo
        if float(self._attributes["hot_water_temperature"]) > 80:
            self._state = "warning"
        else:
            self._state = "ok"
