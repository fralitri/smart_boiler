# custom_components/smart_boiler/sensor.py

import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change, async_call_later
from homeassistant.const import UnitOfPower
from homeassistant.core import callback
from datetime import datetime, timedelta
from .const import DOMAIN  # Importa DOMAIN dal file const.py

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
    entities.append(boiler_state_sensor)

    # Crea i sensori per il tempo di funzionamento
    heating_time_sensor = SmartBoilerTimeSensor(hass, "Tempo Riscaldamento", "riscaldamento", "mdi:radiator")
    acs_time_sensor = SmartBoilerTimeSensor(hass, "Tempo ACS", "acs", "mdi:water-pump")
    total_time_sensor = SmartBoilerTimeSensor(hass, "Tempo Totale", ["acs", "riscaldamento"], "mdi:clock")
    entities.extend([heating_time_sensor, acs_time_sensor, total_time_sensor])

    # Registra le entità in Home Assistant
    async_add_entities(entities, update_before_add=True)

    # Aggiungi un listener per aggiornamenti in tempo reale
    async_track_state_change(
        hass, config_entry.data["power_entity"], boiler_state_sensor.async_update_callback
    )

    # Collega i sensori di tempo al sensore principale
    boiler_state_sensor.set_time_sensors(heating_time_sensor, acs_time_sensor, total_time_sensor)

    # Avvia il timer per aggiornare i sensori di tempo
    async_call_later(hass, 1, boiler_state_sensor._handle_timer)

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
        self._heating_time_sensor = None
        self._acs_time_sensor = None
        self._total_time_sensor = None
        self._update_timer = None
        self._unique_id = f"{DOMAIN}_{name.lower().replace(' ', '_')}"  # ID univoco basato sul nome

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor based on the current state."""
        if self._state == "riscaldamento":
            return "mdi:radiator"
        elif self._state == "acs":
            return "mdi:water-pump"
        elif self._state == "standby":
            return "mdi:power-standby"
        elif self._state == "circolatore":
            return "mdi:reload"
        elif self._state == "errore":
            return "mdi:alert-circle"
        else:
            return "mdi:alert-circle"  # Icona predefinita per stati sconosciuti

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return self._attributes

    async def async_update_callback(self, entity_id, old_state, new_state):
        """Handle state changes for the power sensor."""
        await self.async_update()
        self.async_write_ha_state()  # Aggiorna lo stato in Home Assistant

        # Aggiorna i sensori di tempo
        await self._update_time_sensors()

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

    @callback
    def _handle_timer(self, _):
        """Handle the timer callback to update the time sensors."""
        self._hass.async_create_task(self._update_time_sensors())
        async_call_later(self._hass, 1, self._handle_timer)  # Ripianifica il timer

    async def _update_time_sensors(self):
        """Update the time sensors based on the current state."""
        if self._heating_time_sensor:
            await self._heating_time_sensor.async_update_time(self._state)
        if self._acs_time_sensor:
            await self._acs_time_sensor.async_update_time(self._state)
        if self._total_time_sensor:
            await self._total_time_sensor.async_update_time(self._state)

class SmartBoilerTimeSensor(Entity):
    """Representation of a Smart Boiler Time Sensor."""

    def __init__(self, hass, name, target_states, icon):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._target_states = target_states if isinstance(target_states, list) else [target_states]
        self._icon = icon
        self._state = "00:00:00"  # Formato hh:mm:ss
        self._total_seconds = 0  # Tempo totale in secondi
        self._last_update = datetime.now()
        self._last_state = None
        self._midnight_reset = False  # Flag per il reset a mezzanotte
        self._unique_id = f"{DOMAIN}_{name.lower().replace(' ', '_')}"  # ID univoco basato sul nome

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return None  # Non mostrare unità di misura

    async def async_update_time(self, new_state):
        """Update the time based on the new state."""
        now = datetime.now()

        # Controlla se è mezzanotte e azzera il tempo
        if now.hour == 0 and now.minute == 0 and now.second == 0 and not self._midnight_reset:
            self._total_seconds = 0
            self._state = "00:00:00"
            self._midnight_reset = True
        elif now.hour != 0 or now.minute != 0 or now.second != 0:
            self._midnight_reset = False

        # Calcola il tempo trascorso
        elapsed_time = (now - self._last_update).total_seconds()

        # Aggiorna il tempo solo se lo stato è attivo
        if new_state in self._target_states:
            self._total_seconds += int(elapsed_time)
            self._state = self._seconds_to_hhmmss(self._total_seconds)

        # Aggiorna il timestamp dell'ultimo aggiornamento
        self._last_update = now

        # Log di debug
        _LOGGER.debug(
            f"Sensore {self._name}: Stato={new_state}, Tempo trascorso={elapsed_time}, Tempo totale={self._state}"
        )

        self.async_write_ha_state()

    def _seconds_to_hhmmss(self, total_seconds):
        """Convert seconds to hh:mm:ss."""
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
