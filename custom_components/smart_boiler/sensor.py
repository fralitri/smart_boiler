# custom_components/smart_boiler/sensor.py
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.const import UnitOfPower
from homeassistant.core import callback
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    entities = []

    # Crea i sensori per il tempo di funzionamento
    heating_time_sensor = SmartBoilerTimeSensor(hass, "Tempo Riscaldamento", "heating")
    acs_time_sensor = SmartBoilerTimeSensor(hass, "Tempo ACS", "acs")
    total_time_sensor = SmartBoilerTimeSensor(hass, "Tempo Totale", "total")

    # Crea il sensore "Stato Caldaia" e passa i sensori di tempo
    boiler_state_sensor = SmartBoilerStateSensor(
        hass,
        "Stato Caldaia",
        config_entry.data["power_entity"],
        config_entry.data["power_threshold_standby"],
        config_entry.data["power_threshold_acs"],
        config_entry.data["power_threshold_circulator"],
        config_entry.data["power_threshold_heating"],
        heating_time_sensor,
        acs_time_sensor,
        total_time_sensor,
    )

    # Aggiungi i sensori alla lista delle entità
    entities.extend([boiler_state_sensor, heating_time_sensor, acs_time_sensor, total_time_sensor])

    # Registra le entità in Home Assistant
    async_add_entities(entities, update_before_add=True)

    # Aggiungi un listener per aggiornamenti in tempo reale
    async_track_state_change(
        hass, config_entry.data["power_entity"], boiler_state_sensor.async_update_callback
    )

class SmartBoilerStateSensor(Entity):
    """Representation of the Smart Boiler State Sensor."""

    def __init__(self, hass, name, power_entity, threshold_standby, threshold_acs, threshold_circulator, threshold_heating, heating_time_sensor, acs_time_sensor, total_time_sensor):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._power_entity = power_entity
        self._threshold_standby = threshold_standby
        self._threshold_acs = threshold_acs
        self._threshold_circulator = threshold_circulator
        self._threshold_heating = threshold_heating
        self._state = None
        self._attributes = {}
        self._heating_time_sensor = heating_time_sensor
        self._acs_time_sensor = acs_time_sensor
        self._total_time_sensor = total_time_sensor

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

    async def async_update_callback(self, entity_id, old_state, new_state):
        """Handle state changes for the power sensor."""
        await self.async_update()
        self.async_write_ha_state()  # Aggiorna lo stato in Home Assistant

        # Aggiorna i sensori di tempo
        await self._heating_time_sensor.async_update_time(self._state)
        await self._acs_time_sensor.async_update_time(self._state)
        await self._total_time_sensor.async_update_time(self._state)

    async def async_update(self):
        """Fetch new state data for the sensor."""
        power_state = self._hass.states.get(self._power_entity)
        if power_state is None or power_state.state in ["unknown", "unavailable"]:
            self._state = "errore"
            return

        try:
            power = float(power_state.state)
        except (ValueError, TypeError):
            self._state = "errore"
            return

        # Determina lo stato della caldaia
        if power < self._threshold_standby:
            self._state = "standby"
        elif self._threshold_standby <= power < self._threshold_acs:
            self._state = "acs"
        elif self._threshold_acs <= power < self._threshold_circulator:
            self._state = "circolatore"
        elif self._threshold_circulator <= power < self._threshold_heating:
            self._state = "riscaldamento"
        else:
            self._state = "errore"

        # Aggiorna gli attributi
        self._attributes = {
            "power": power,
            "threshold_standby": self._threshold_standby,
            "threshold_acs": self._threshold_acs,
            "threshold_circulator": self._threshold_circulator,
            "threshold_heating": self._threshold_heating,
        }

class SmartBoilerTimeSensor(Entity):
    """Representation of a Smart Boiler Time Sensor."""

    def __init__(self, hass, name, mode):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._mode = mode
        self._state = 0  # Tempo in secondi
        self._last_update = datetime.now()
        self._last_state = None

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
        return "s"

    async def async_update_time(self, new_state):
        """Update the time based on the new state."""
        now = datetime.now()
        elapsed_time = (now - self._last_update).total_seconds()

        # Aggiorna il tempo solo se lo stato è cambiato
        if self._last_state != new_state:
            self._last_update = now
            self._last_state = new_state

        # Calcola il tempo in base alla modalità
        if self._mode == "total" and new_state in ["acs", "heating"]:
            self._state += elapsed_time
        elif self._mode == "acs" and new_state == "acs":
            self._state += elapsed_time
        elif self._mode == "heating" and new_state == "riscaldamento":
            self._state += elapsed_time

        # Log di debug
        _LOGGER.debug(
            f"Sensore {self._name}: Stato={new_state}, Tempo trascorso={elapsed_time}, Tempo totale={self._state}"
        )

        self.async_write_ha_state()
