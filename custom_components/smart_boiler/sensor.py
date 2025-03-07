# custom_components/smart_boiler/sensor.py
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change, async_call_later
from homeassistant.const import UnitOfPower
from homeassistant.core import callback
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    entities = []

    # Create the "Boiler State" sensor
    boiler_state_sensor = SmartBoilerStateSensor(
        hass,
        "Boiler State",
        config_entry.data["power_entity"],
        config_entry.data["power_threshold_standby"],
        config_entry.data["power_threshold_acs"],
        config_entry.data["power_threshold_circulator"],
        config_entry.data["power_threshold_heating"],
    )

    # Add the main sensor to the entities list
    entities.append(boiler_state_sensor)

    # Create the time sensors
    heating_time_sensor = SmartBoilerTimeSensor(hass, "Heating Time", "heating", "mdi:radiator")
    acs_time_sensor = SmartBoilerTimeSensor(hass, "ACS Time", "acs", "mdi:water-pump")
    total_time_sensor = SmartBoilerTimeSensor(hass, "Total Time", ["acs", "heating"], "mdi:clock")

    # Add the time sensors to the entities list
    entities.extend([heating_time_sensor, acs_time_sensor, total_time_sensor])

    # Register the entities in Home Assistant
    async_add_entities(entities, update_before_add=True)

    # Add a listener for real-time updates
    async_track_state_change(
        hass, config_entry.data["power_entity"], boiler_state_sensor.async_update_callback
    )

    # Link the time sensors to the main sensor
    boiler_state_sensor.set_time_sensors(heating_time_sensor, acs_time_sensor, total_time_sensor)

    # Start the timer to update the time sensors
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

    def set_time_sensors(self, heating_time_sensor, acs_time_sensor, total_time_sensor):
        """Set the time sensors."""
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
    def icon(self):
        """Return the icon of the sensor based on the current state."""
        if self._state == "heating":
            return "mdi:radiator"
        elif self._state == "acs":
            return "mdi:water-pump"
        elif self._state == "standby":
            return "mdi:power-standby"
        elif self._state == "circulator":
            return "mdi:reload"
        elif self._state == "error":
            return "mdi:alert-circle"
        else:
            return "mdi:alert-circle"  # Default icon for unknown states

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return self._attributes

    async def async_update_callback(self, entity_id, old_state, new_state):
        """Handle state changes for the power sensor."""
        await self.async_update()
        self.async_write_ha_state()  # Update the state in Home Assistant

        # Update the time sensors
        await self._update_time_sensors()

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

        # Update the attributes
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
        async_call_later(self._hass, 1, self._handle_timer)  # Reschedule the timer

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
        self._state = "00:00:00"  # Format hh:mm:ss
        self._total_seconds = 0  # Total time in seconds
        self._last_update = datetime.now()
        self._last_state = None
        self._midnight_reset = False  # Flag for midnight reset

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
        return None  # Do not show unit of measurement

    async def async_update_time(self, new_state):
        """Update the time based on the new state."""
        now = datetime.now()

        # Check if it's midnight and reset the time
        if now.hour == 0 and now.minute == 0 and now.second == 0 and not self._midnight_reset:
            self._total_seconds = 0
            self._state = "00:00:00"
            self._midnight_reset = True
        elif now.hour != 0 or now.minute != 0 or now.second != 0:
            self._midnight_reset = False

        # Calculate elapsed time
        elapsed_time = (now - self._last_update).total_seconds()

        # Update the time only if the state is active
        if new_state in self._target_states:
            self._total_seconds += int(elapsed_time)
            self._state = self._seconds_to_hhmmss(self._total_seconds)

        # Update the last update timestamp
        self._last_update = now

        # Debug log
        _LOGGER.debug(
            f"Sensor {self._name}: State={new_state}, Elapsed time={elapsed_time}, Total time={self._state}"
        )

        self.async_write_ha_state()

    def _seconds_to_hhmmss(self, total_seconds):
        """Convert seconds to hh:mm:ss."""
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
