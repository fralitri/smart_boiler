import logging
from datetime import timedelta, datetime
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change, async_call_later
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = 1  # Update every 1 second


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    state_unique_id = f"{config_entry.entry_id}_boiler_state"
    time_unique_id = f"{config_entry.entry_id}_acs_time"

    boiler_state_sensor = SmartBoilerStateSensor(
        hass,
        "Boiler State",
        state_unique_id,
        config_entry.data["power_entity"],
        config_entry.data["power_threshold_standby"],
        config_entry.data["power_threshold_acs"],
        config_entry.data["power_threshold_circulator"],
        config_entry.data["power_threshold_heating"],
    )

    acs_time_sensor = SmartBoilerAcsTimeSensor(
        hass,
        "ACS Time",
        time_unique_id,
        config_entry.data["power_entity"]
    )

    async_add_entities([boiler_state_sensor, acs_time_sensor], update_before_add=True)

    # Add a listener to track real-time state changes for the ACS sensor
    async_track_state_change(
        hass, config_entry.data["power_entity"], acs_time_sensor.async_update_callback
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
        icons = {
            "heating": "mdi:radiator",
            "acs": "mdi:water-pump",
            "standby": "mdi:power-standby",
            "circulator": "mdi:reload",
            "error": "mdi:alert-circle",
        }
        return icons.get(self._state, "mdi:alert-circle")

    async def async_update_callback(self, entity_id, old_state, new_state):
        """Handle state changes for the power sensor."""
        await self.async_update()
        self.async_write_ha_state()

    async def async_update(self):
        """Fetch new state data for the sensor."""
        power_state = self._hass.states.get(self._power_entity)
        if power_state is None or power_state.state in ["unknown", "unavailable"]:
            self._state = "error"
            return

        try:
            power = float(power_state.state)
        except (ValueError, TypeError):
            self._state = "error"
            return

        # Determine the boiler state
        if power < self._threshold_standby:
            self._state = "standby"
        elif self._threshold_standby <= power < self._threshold_acs:
            self._state = "acs"
        elif self._threshold_acs <= power < self._threshold_circulator:
            self._state = "circulator"
        elif self._threshold_circulator <= power < self._threshold_heating:
            self._state = "heating"
        else:
            self._state = "error"


class SmartBoilerAcsTimeSensor(Entity):
    """Representation of the ACS Time Sensor."""

    def __init__(self, hass, name, unique_id, power_entity):
        """Initialize the ACS time sensor."""
        self._hass = hass
        self._name = name
        self._unique_id = unique_id
        self._power_entity = power_entity
        self._state = "00:00:00"
        self._start_time = None
        self._total_time = timedelta()
        self._time_series = []

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
        """Return the current state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return an icon for the sensor."""
        return "mdi:chart-timeline-variant"

    @property
    def extra_state_attributes(self):
        """Return additional attributes for the sensor."""
        return {"time_series": self._time_series}

    async def async_update_callback(self, entity_id, old_state, new_state):
        """Handle state changes for the power sensor."""
        if new_state and new_state.state == "acs":
            # Start tracking ACS time
            if self._start_time is None:
                self._start_time = datetime.now()
                self._update_time_series()
        elif self._start_time:
            # Stop tracking and calculate total time
            self._total_time += datetime.now() - self._start_time
            self._start_time = None

        await self.async_update()
        self.async_write_ha_state()

    def _update_time_series(self):
        """Update the time series for graph visualization."""
        if self._start_time:
            current_time = datetime.now() - self._start_time + self._total_time
        else:
            current_time = self._total_time

        self._time_series.append(
            {
                "timestamp": datetime.now().isoformat(),
                "acs_time": str(current_time).split(".")[0],  # Format hh:mm:ss
            }
        )

        # Keep the time series limited (e.g., last 100 entries)
        self._time_series = self._time_series[-100:]

    async def async_update(self):
        """Update the sensor's state."""
        if self._start_time:
            elapsed = datetime.now() - self._start_time
            current_time = self._total_time + elapsed
        else:
            current_time = self._total_time

        # Format time as hh:mm:ss
        self._state = str(current_time).split(".")[0]
