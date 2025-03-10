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
        config_entry.entry_id,  # Usa l'ID della configurazione per il unique_id
    )
    entities.append(boiler_state_sensor)

    # Crea i sensori per il tempo di funzionamento
    heating_time_sensor = SmartBoilerTimeSensor(
        hass,
        "Tempo Riscaldamento",
        "riscaldamento",
        "mdi:radiator",
        config_entry.entry_id,  # Usa l'ID della configurazione per il unique_id
    )
    acs_time_sensor = SmartBoilerTimeSensor(
        hass,
        "Tempo ACS",
        "acs",
        "mdi:water-pump",
        config_entry.entry_id,  # Usa l'ID della configurazione per il unique_id
    )
    total_time_sensor = SmartBoilerTimeSensor(
        hass,
        "Tempo Totale",
        ["acs", "riscaldamento"],
        "mdi:clock",
        config_entry.entry_id,  # Usa l'ID della configurazione per il unique_id
    )
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

    def __init__(self, hass, name, power_entity, threshold_standby, threshold_acs, threshold_circulator, threshold_heating, config_entry_id):
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
        self._unique_id = f"{config_entry_id}_{name.lower().replace(' ', '_')}"  # ID univoco basato sull'ID della configurazione e sul nome

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    # Resto del codice rimane invariato...

class SmartBoilerTimeSensor(Entity):
    """Representation of a Smart Boiler Time Sensor."""

    def __init__(self, hass, name, target_states, icon, config_entry_id):
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
        self._unique_id = f"{config_entry_id}_{name.lower().replace(' ', '_')}"  # ID univoco basato sull'ID della configurazione e sul nome

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    # Resto del codice rimane invariato...
