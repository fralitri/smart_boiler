# custom_components/smart_boiler/sensor.py
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.const import STATE_ON
from datetime import datetime, timedelta

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

    # Crea i sensori di tempo utilizzando history_stats
    heating_time_sensor = await create_history_stats_sensor(
        hass,
        "Tempo Riscaldamento",
        boiler_state_sensor.entity_id,
        "riscaldamento",
        "mdi:radiator"
    )
    acs_time_sensor = await create_history_stats_sensor(
        hass,
        "Tempo ACS",
        boiler_state_sensor.entity_id,
        "acs",
        "mdi:water-pump"
    )
    total_time_sensor = await create_history_stats_sensor(
        hass,
        "Tempo Totale",
        boiler_state_sensor.entity_id,
        ["acs", "riscaldamento"],
        "mdi:clock"
    )

    # Aggiungi i sensori di tempo alla lista delle entità
    entities.extend([heating_time_sensor, acs_time_sensor, total_time_sensor])

    # Registra le entità in Home Assistant
    async_add_entities(entities, update_before_add=True)

    # Aggiungi un listener per aggiornamenti in tempo reale
    async_track_state_change(
        hass, config_entry.data["power_entity"], boiler_state_sensor.async_update_callback
    )

async def create_history_stats_sensor(hass, name, entity_id, target_state, icon):
    """Crea un sensore history_stats per calcolare il tempo di funzionamento."""
    sensor = HistoryStatsSensor(hass, name, entity_id, target_state, icon)
    await sensor.async_update()
    return sensor

class HistoryStatsSensor(Entity):
    """Rappresentazione di un sensore history_stats personalizzato."""

    def __init__(self, hass, name, entity_id, target_state, icon):
        """Inizializza il sensore."""
        self._hass = hass
        self._name = name
        self._entity_id = entity_id
        self._target_state = target_state if isinstance(target_state, list) else [target_state]
        self._icon = icon
        self._state = 0  # Tempo totale in secondi

    @property
    def name(self):
        """Restituisce il nome del sensore."""
        return self._name

    @property
    def state(self):
        """Restituisce lo stato del sensore."""
        return self._state

    @property
    def icon(self):
        """Restituisce l'icona del sensore."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """Restituisce l'unità di misura."""
        return "s"  # Secondi

    @property
    def state_class(self):
        """Restituisce la classe dello stato."""
        return "total_increasing"  # Indica che il valore aumenta nel tempo

    @property
    def device_class(self):
        """Restituisce la classe del dispositivo."""
        return "duration"  # Indica che il sensore misura una durata

    async def async_update(self):
        """Aggiorna il sensore calcolando il tempo di funzionamento."""
        now = datetime.now()
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Calcola il tempo di funzionamento utilizzando history_stats
        time_on = 0
        for state in self._target_state:
            history = await self._hass.async_add_executor_job(
                self._hass.states.get_history,
                self._entity_id,
                start_time,
                now,
                False,
                False,
            )
            for entry in history:
                if entry.state == state:
                    time_on += (entry.last_updated - entry.last_changed).total_seconds()

        self._state = int(time_on)
        self.async_write_ha_state()
