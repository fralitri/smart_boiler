# custom_components/smart_boiler/sensor.py
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.const import UnitOfPower

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    entities = []

    # Debug: Stampa le soglie configurate
    _LOGGER.debug(f"Soglie configurate: standby={config_entry.data['power_threshold_standby']}, acs={config_entry.data['power_threshold_acs']}, circolatore={config_entry.data['power_threshold_circulator']}, riscaldamento={config_entry.data['power_threshold_heating']}")

    # Crea il sensore "Stato Caldaia"
    boiler_state_sensor = SmartBoilerStateSensor(
        "Stato Caldaia",
        config_entry.data["power_entity"],
        config_entry.data["power_threshold_standby"],
        config_entry.data["power_threshold_acs"],
        config_entry.data["power_threshold_circulator"],
        config_entry.data["power_threshold_heating"],
    )

    # Debug: Verifica che il sensore sia stato creato
    _LOGGER.debug(f"Sensore 'Stato Caldaia' creato: {boiler_state_sensor.name}")

    # Aggiungi il sensore alla lista delle entità
    entities.append(boiler_state_sensor)

    # Registra le entità in Home Assistant
    async_add_entities(entities)

class SmartBoilerStateSensor(Entity):
    """Representation of the Smart Boiler State Sensor."""

    def __init__(self, name, power_entity, threshold_standby, threshold_acs, threshold_circulator, threshold_heating):
        """Initialize the sensor."""
        self._name = name
        self._power_entity = power_entity
        self._threshold_standby = threshold_standby
        self._threshold_acs = threshold_acs
        self._threshold_circulator = threshold_circulator
        self._threshold_heating = threshold_heating
        self._state = None
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
        power_state = self.hass.states.get(self._power_entity)
        if power_state is None or power_state.state in ["unknown", "unavailable"]:
            _LOGGER.warning(f"Sensore di potenza {self._power_entity} non valido: {power_state.state}")
            self._state = "errore"
            return

        try:
            power = float(power_state.state)
        except (ValueError, TypeError):
            _LOGGER.warning(f"Valore di potenza non valido: {power_state.state}")
            self._state = "errore"
            return

        # Debug: Stampa i valori di potenza e soglie
        _LOGGER.debug(f"Potenza: {power} W, Soglie: standby={self._threshold_standby}, acs={self._threshold_acs}, circolatore={self._threshold_circulator}, riscaldamento={self._threshold_heating}")

        # Determina lo stato della caldaia
        if power < self._threshold_standby:
            self._state = "standby"
        elif self._threshold_standby <= power < self._threshold_acs:
            self._state = "acs"
        elif self._threshold_acs <= power < self._threshold_circulator:
            self._state = "circolatore"
            _LOGGER.debug(f"Stato Caldaia determinato: circolatore (potenza={power} W)")
        elif self._threshold_circulator <= power < self._threshold_heating:
            self._state = "riscaldamento"
        else:
            self._state = "errore"

        # Debug: Stampa lo stato determinato
        _LOGGER.debug(f"Stato Caldaia determinato: {self._state}")

        # Aggiorna gli attributi
        self._attributes = {
            "power": power,
            "threshold_standby": self._threshold_standby,
            "threshold_acs": self._threshold_acs,
            "threshold_circulator": self._threshold_circulator,
            "threshold_heating": self._threshold_heating,
        }
