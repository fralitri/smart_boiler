# custom_components/smart_boiler/sensor.py

import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.core import callback
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.components.template.sensor import SensorTemplate
from homeassistant.components.history_stats.sensor import HistoryStatsSensor
from .const import (
    DOMAIN,
    DEFAULT_POWER_THRESHOLD_STANDBY,
    DEFAULT_POWER_THRESHOLD_ACS,
    DEFAULT_POWER_THRESHOLD_CIRCULATOR,
    DEFAULT_POWER_THRESHOLD_HEATING,
    SENSOR_HEATING_TIME,
    SENSOR_ACS_TIME,
    SENSOR_TOTAL_TIME,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    entities = []

    # Crea il sensore "Stato Caldaia"
    boiler_state_sensor = SmartBoilerStateSensor(
        hass,
        "Stato Caldaia",
        config_entry.data["power_entity"],
        config_entry.data.get("power_threshold_standby", DEFAULT_POWER_THRESHOLD_STANDBY),
        config_entry.data.get("power_threshold_acs", DEFAULT_POWER_THRESHOLD_ACS),
        config_entry.data.get("power_threshold_circulator", DEFAULT_POWER_THRESHOLD_CIRCULATOR),
        config_entry.data.get("power_threshold_heating", DEFAULT_POWER_THRESHOLD_HEATING),
    )
    entities.append(boiler_state_sensor)

    # Crea i sensori di tempo utilizzando HistoryStats e Template Sensor
    entities.extend(create_time_sensors(hass, config_entry))

    # Registra le entità in Home Assistant
    async_add_entities(entities, update_before_add=True)

    # Aggiungi un listener per aggiornamenti in tempo reale
    async_track_state_change(
        hass, config_entry.data["power_entity"], boiler_state_sensor.async_update_callback
    )

def create_time_sensors(hass, config_entry):
    """Crea i sensori di tempo utilizzando HistoryStats e Template Sensor."""
    entities = []

    # Configurazione per i sensori HistoryStats
    history_stats_config = {
        "platform": "history_stats",
        "entity_id": config_entry.data["power_entity"],
        "start": "{{ today_at() }}",
        "end": "{{ now() }}",
        "type": "time",
    }

    # Sensore "Tempo Riscaldamento"
    heating_time_sensor = HistoryStatsSensor(
        hass,
        {
            **history_stats_config,
            "name": SENSOR_HEATING_TIME,
            "state": "riscaldamento",
            CONF_UNIQUE_ID: f"{DOMAIN}_{SENSOR_HEATING_TIME}",
        },
    )
    entities.append(heating_time_sensor)

    # Sensore "Tempo ACS"
    acs_time_sensor = HistoryStatsSensor(
        hass,
        {
            **history_stats_config,
            "name": SENSOR_ACS_TIME,
            "state": "acs",
            CONF_UNIQUE_ID: f"{DOMAIN}_{SENSOR_ACS_TIME}",
        },
    )
    entities.append(acs_time_sensor)

    # Sensore "Tempo Totale"
    total_time_sensor = HistoryStatsSensor(
        hass,
        {
            **history_stats_config,
            "name": SENSOR_TOTAL_TIME,
            "state": ["riscaldamento", "acs"],
            CONF_UNIQUE_ID: f"{DOMAIN}_{SENSOR_TOTAL_TIME}",
        },
    )
    entities.append(total_time_sensor)

    # Configurazione per i sensori Template
    template_config = {
        "platform": "template",
        "sensors": {
            "tempo_riscaldamento_formattato": {
                "friendly_name": "Tempo Riscaldamento (hh:mm:ss)",
                "value_template": '{% set hours = states("sensor.tempo_riscaldamento") | float %}'
                                 '{{ "%02d:%02d:%02d" | format(hours // 1, (hours % 1 * 60) // 1, (hours % 1 * 3600) % 60) }}',
                "icon": "mdi:radiator",
                CONF_UNIQUE_ID: f"{DOMAIN}_tempo_riscaldamento_formattato",
            },
            "tempo_acs_formattato": {
                "friendly_name": "Tempo ACS (hh:mm:ss)",
                "value_template": '{% set hours = states("sensor.tempo_acs") | float %}'
                                 '{{ "%02d:%02d:%02d" | format(hours // 1, (hours % 1 * 60) // 1, (hours % 1 * 3600) % 60) }}',
                "icon": "mdi:water-pump",
                CONF_UNIQUE_ID: f"{DOMAIN}_tempo_acs_formattato",
            },
            "tempo_totale_formattato": {
                "friendly_name": "Tempo Totale (hh:mm:ss)",
                "value_template": '{% set hours = states("sensor.tempo_totale") | float %}'
                                 '{{ "%02d:%02d:%02d" | format(hours // 1, (hours % 1 * 60) // 1, (hours % 1 * 3600) % 60) }}',
                "icon": "mdi:clock",
                CONF_UNIQUE_ID: f"{DOMAIN}_tempo_totale_formattato",
            },
        },
    }

    # Aggiungi i sensori template
    for sensor_name, sensor_config in template_config["sensors"].items():
        template_sensor = SensorTemplate(
            hass,
            sensor_config,
            sensor_name,
        )
        entities.append(template_sensor)

    return entities

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
        self._unique_id = f"{DOMAIN}_{name.lower().replace(' ', '_')}"

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
            return "mdi:alert-circle"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return self._attributes

    async def async_update_callback(self, entity_id, old_state, new_state):
        """Handle state changes for the power sensor."""
        await self.async_update()
        self.async_write_ha_state()

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
