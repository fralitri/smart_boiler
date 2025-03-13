# custom_components/smart_boiler/sensor.py
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.core import callback
from homeassistant.const import STATE_UNKNOWN
from homeassistant.util import dt as dt_util
import asyncio

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    power_entity = config_entry.data["power_entity"]
    unique_id_prefix = config_entry.entry_id

    # Crea il sensore per lo Stato Caldaia
    boiler_state_sensor = SmartBoilerStateSensor(
        hass,
        "Stato Caldaia",
        f"{unique_id_prefix}_boiler_state",
        power_entity,
        config_entry.data["power_threshold_standby"],
        config_entry.data["power_threshold_acs"],
        config_entry.data["power_threshold_circulator"],
        config_entry.data["power_threshold_heating"],
    )

    # Crea i sensori per ACS, Riscaldamento e Totale
    sensors = [
        boiler_state_sensor,
        SmartBoilerTimeSensor(hass, "Tempo ACS Caldaia", f"{unique_id_prefix}_tempo_acs", boiler_state_sensor, "acs"),
        SmartBoilerTimeSensor(hass, "Tempo Riscaldamento Caldaia", f"{unique_id_prefix}_tempo_riscaldamento", boiler_state_sensor, "riscaldamento"),
        SmartBoilerTotalTimeSensor(hass, "Tempo Totale Caldaia", f"{unique_id_prefix}_tempo_totale"),
    ]

    # Aggiungi i sensori alla lista delle entità
    async_add_entities(sensors, update_before_add=True)

    # Aggiungi un listener per aggiornamenti in tempo reale
    async_track_state_change(
        hass, power_entity, boiler_state_sensor.async_update_callback
    )

class SmartBoilerStateSensor(Entity):
    """Representation of the Smart Boiler State Sensor."""

    def __init__(self, hass, name, unique_id, power_entity, threshold_standby, threshold_acs, threshold_circulator, threshold_heating):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._unique_id = unique_id
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
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

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
        if power_state is None or power_state.state in [STATE_UNKNOWN, "unavailable"]:
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
    """Representation of a Smart Boiler Time Sensor (ACS or Riscaldamento)."""

    def __init__(self, hass, name, unique_id, boiler_state_sensor, state_to_track):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._unique_id = unique_id
        self._boiler_state_sensor = boiler_state_sensor
        self._state_to_track = state_to_track
        self._state = 0  # Tempo accumulato in secondi
        self._last_update = dt_util.utcnow()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return int(self._state)  # Rimuove i decimali

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "s"  # Tempo in secondi

    @property
    def icon(self):
        """Return the icon of the sensor."""
        if self._state_to_track == "acs":
            return "mdi:water-pump"  # Icona per ACS
        else:
            return "mdi:radiator"  # Icona per Riscaldamento

    async def async_added_to_hass(self):
        """Call when entity is added to hass."""
        await super().async_added_to_hass()
        self._last_update = dt_util.utcnow()
        async_track_state_change(self._hass, self._boiler_state_sensor.entity_id, self.async_update_callback)
        self._hass.async_create_task(self.async_periodic_update())

    @callback
    async def async_update_callback(self, entity_id, old_state, new_state):
        """Handle state changes for the boiler state sensor."""
        await self.async_update()
        self.async_write_ha_state()

    async def async_update(self):
        """Fetch new state data for the sensor."""
        now = dt_util.utcnow()
        time_diff = (now - self._last_update).total_seconds()

        # Se la caldaia è nello stato che stiamo tracciando, aggiungi il tempo
        if self._boiler_state_sensor.state == self._state_to_track:
            self._state += time_diff

        self._last_update = now
        self.async_write_ha_state()

    async def async_periodic_update(self):
        """Force periodic updates every 10 seconds."""
        while True:
            await self.async_update()
            await asyncio.sleep(10)  # Aggiorna ogni 10 secondi

class SmartBoilerTotalTimeSensor(Entity):
    """Representation of the Smart Boiler Total Time Sensor (ACS + Riscaldamento)."""

    def __init__(self, hass, name, unique_id):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._unique_id = unique_id
        self._state = 0  # Tempo accumulato in secondi

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return int(self._state)  # Rimuove i decimali

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "s"  # Tempo in secondi

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:clock"  # Icona per il tempo totale

    async def async_added_to_hass(self):
        """Call when entity is added to hass."""
        await super().async_added_to_hass()
        self._hass.async_create_task(self.async_update_total_time())

    async def async_update_total_time(self):
        """Update the total time by summing ACS and Riscaldamento time."""
        while True:
            acs_time = float(self._hass.states.get(f"sensor.{self._unique_id.replace('_totale', '_acs')}").state or 0)
            riscaldamento_time = float(self._hass.states.get(f"sensor.{self._unique_id.replace('_totale', '_riscaldamento')}").state or 0)
            self._state = acs_time + riscaldamento_time
            self.async_write_ha_state()
            await asyncio.sleep(10)  # Aggiorna ogni 10 secondi
