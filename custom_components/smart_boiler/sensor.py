# custom_components/smart_boiler/sensor.py
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.const import UnitOfPower
from homeassistant.core import callback
from datetime import datetime, timedelta
from homeassistant.components.recorder import history

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    entities = []

    # Crea il sensore "Stato Caldaia"
    boiler_state_sensor = SmartBoilerStateSensor(
        hass,
        "Stato Caldaia",
        config_entry.data["power_entity"],
        config_entry.data["power_threshold_standby"],
        config_entry.data["power_threshold_acs"],
        config_entry.data["power_threshold_circulator"],
        config_entry.data["power_threshold_heating"],
    )

    # Crea i sensori per il tempo di funzionamento
    heating_time_sensor = SmartBoilerTimeSensor(hass, "Tempo Riscaldamento", "riscaldamento", boiler_state_sensor)
    acs_time_sensor = SmartBoilerTimeSensor(hass, "Tempo ACS", "acs", boiler_state_sensor)
    total_time_sensor = SmartBoilerTimeSensor(hass, "Tempo Totale", "total", boiler_state_sensor)

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

    def __init__(self, hass, name, power_entity, threshold_standby, threshold_acs, threshold_circulator, threshold_heating):
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

    def __init__(self, hass, name, mode, state_sensor):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._mode = mode
        self._state_sensor = state_sensor
        self._state = 0  # Tempo in secondi
        self._last_update = datetime.now()

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

    async def async_update(self):
        """Fetch new state data for the sensor."""
        now = datetime.now()
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)  # Inizio del giorno
        end_time = now  # Fine del periodo di calcolo

        # Ottieni la cronologia degli stati della caldaia
        history_list = await history.state_changes_during_period(
            self._hass, start_time, end_time, self._state_sensor.entity_id
        )

        if not history_list:
            return

        # Calcola il tempo trascorso nello stato desiderato
        total_time = timedelta()
        previous_state = None
        previous_time = start_time

        for state in history_list.get(self._state_sensor.entity_id, []):
            current_state = state.state
            current_time = state.last_changed

            if previous_state is not None:
                if self._mode == "total" and previous_state in ["acs", "riscaldamento"]:
                    total_time += current_time - previous_time
                elif self._mode == "acs" and previous_state == "acs":
                    total_time += current_time - previous_time
                elif self._mode == "heating" and previous_state == "riscaldamento":
                    total_time += current_time - previous_time

            previous_state = current_state
            previous_time = current_time

        # Aggiungi il tempo dall'ultimo stato fino a ora
        if previous_state is not None:
            if self._mode == "total" and previous_state in ["acs", "riscaldamento"]:
                total_time += end_time - previous_time
            elif self._mode == "acs" and previous_state == "acs":
                total_time += end_time - previous_time
            elif self._mode == "heating" and previous_state == "riscaldamento":
                total_time += end_time - previous_time

        # Aggiorna lo stato del sensore
        self._state = int(total_time.total_seconds())

        # Log di debug
        _LOGGER.debug(
            f"Sensore {self._name}: Tempo totale={self._state}"
        )

        self.async_write_ha_state()
