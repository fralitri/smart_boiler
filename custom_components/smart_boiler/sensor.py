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

    # Aggiungi il sensore principale alla lista delle entità
    entities.append(boiler_state_sensor)

    # Registra le entità in Home Assistant
    async_add_entities(entities, update_before_add=True)

    # Aggiungi un listener per aggiornamenti in tempo reale
    async_track_state_change(
        hass, config_entry.data["power_entity"], boiler_state_sensor.async_update_callback
    )

    # Crea i sensori di tempo utilizzando history_stats
    await _create_history_stats_sensors(hass, boiler_state_sensor.entity_id, async_add_entities)

async def _create_history_stats_sensors(hass, entity_id, async_add_entities):
    """Create history_stats sensors for boiler time tracking."""
    from homeassistant.components.history_stats.sensor import HistoryStatsSensor

    # Configura i sensori di tempo
    sensors_config = [
        {
            "unique_id": "tempo_riscaldamento",
            "name": "Tempo Riscaldamento",
            "entity_id": entity_id,
            "state": "riscaldamento",
            "type": "time",
            "start": "{{ now().replace(hour=0, minute=0, second=0) }}",
            "end": "{{ now() }}",
        },
        {
            "unique_id": "tempo_acs",
            "name": "Tempo ACS",
            "entity_id": entity_id,
            "state": "acs",
            "type": "time",
            "start": "{{ now().replace(hour=0, minute=0, second=0) }}",
            "end": "{{ now() }}",
        },
        {
            "unique_id": "tempo_totale",
            "name": "Tempo Totale",
            "entity_id": entity_id,
            "state": ["acs", "riscaldamento"],
            "type": "time",
            "start": "{{ now().replace(hour=0, minute=0, second=0) }}",
            "end": "{{ now() }}",
        },
    ]

    # Crea i sensori di tempo
    for config in sensors_config:
        sensor = HistoryStatsSensor(
            hass,
            config["unique_id"],
            config["name"],
            config["entity_id"],
            config["state"],
            config["type"],
            config["start"],
            config["end"],
        )
        async_add_entities([sensor], True)

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
