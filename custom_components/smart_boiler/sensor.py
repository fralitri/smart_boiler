# custom_components/smart_boiler/sensor.py
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.core import callback
from homeassistant.const import STATE_UNKNOWN
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    power_entity = config_entry.data["power_entity"]
    unique_id_prefix = config_entry.entry_id

    # Crea i sensori per ACS, Riscaldamento e Totale
    sensors = [
        SmartBoilerTimeSensor(hass, "Tempo ACS Caldaia", f"{unique_id_prefix}_tempo_acs", power_entity, "acs"),
        SmartBoilerTimeSensor(hass, "Tempo Riscaldamento Caldaia", f"{unique_id_prefix}_tempo_riscaldamento", power_entity, "riscaldamento"),
        SmartBoilerTotalTimeSensor(hass, "Tempo Totale Caldaia", f"{unique_id_prefix}_tempo_totale", power_entity),
    ]

    # Aggiungi i sensori alla lista delle entità
    async_add_entities(sensors, update_before_add=True)

class SmartBoilerTimeSensor(Entity):
    """Representation of a Smart Boiler Time Sensor (ACS or Riscaldamento)."""

    def __init__(self, hass, name, unique_id, power_entity, state_to_track):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._unique_id = unique_id
        self._power_entity = power_entity
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
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "s"  # Tempo in secondi

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:clock" if self._state_to_track == "acs" else "mdi:radiator"

    async def async_added_to_hass(self):
        """Call when entity is added to hass."""
        await super().async_added_to_hass()
        self._last_update = dt_util.utcnow()
        async_track_state_change(self._hass, self._power_entity, self.async_update_callback)

    @callback
    async def async_update_callback(self, entity_id, old_state, new_state):
        """Handle state changes for the power sensor."""
        if new_state is None or new_state.state in [STATE_UNKNOWN, "unavailable"]:
            return

        now = dt_util.utcnow()
        time_diff = (now - self._last_update).total_seconds()

        # Se la caldaia è nello stato che stiamo tracciando, aggiungi il tempo
        if new_state.state == self._state_to_track:
            self._state += time_diff

        self._last_update = now
        self.async_write_ha_state()

class SmartBoilerTotalTimeSensor(Entity):
    """Representation of the Smart Boiler Total Time Sensor (ACS + Riscaldamento)."""

    def __init__(self, hass, name, unique_id, power_entity):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._unique_id = unique_id
        self._power_entity = power_entity
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
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "s"  # Tempo in secondi

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:clock-check"

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
            await asyncio.sleep(60)  # Aggiorna ogni minuto
