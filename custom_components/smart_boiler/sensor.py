# custom_components/smart_boiler/sensor.py
import logging
from datetime import timedelta, datetime
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change, async_call_later
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = 1  # Aggiornamento ogni 1 secondo


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    unique_id = f"{config_entry.entry_id}_acs_time"
    acs_time_sensor = SmartBoilerAcsTimeSensor(
        hass,
        "ACS Time",
        unique_id,
        config_entry.data["power_entity"]
    )

    async_add_entities([acs_time_sensor], update_before_add=True)

    # Add a listener to track real-time state changes
    async_track_state_change(
        hass, config_entry.data["power_entity"], acs_time_sensor.async_update_callback
    )


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
        self._cancel_update = None

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
        return "mdi:timer"

    async def async_update_callback(self, entity_id, old_state, new_state):
        """Handle state changes for the power sensor."""
        if new_state and new_state.state == "acs":
            # Start tracking ACS time
            if self._start_time is None:
                self._start_time = datetime.now()
                self._start_periodic_update()
        elif self._start_time:
            # Stop tracking and calculate total time
            self._total_time += datetime.now() - self._start_time
            self._start_time = None
            if self._cancel_update:
                self._cancel_update()
                self._cancel_update = None

        await self.async_update()
        self.async_write_ha_state()

    def _start_periodic_update(self):
        """Start periodic updates while in ACS state."""
        @callback
        def _update(_):
            if self._start_time:
                # Calculate current total time including ongoing period
                elapsed = datetime.now() - self._start_time
                current_time = self._total_time + elapsed
                self._state = str(current_time).split(".")[0]  # Format hh:mm:ss
                self.async_write_ha_state()

                # Schedule the next update
                self._cancel_update = async_call_later(
                    self._hass, UPDATE_INTERVAL, _update
                )

        # Start the first update
        self._cancel_update = async_call_later(self._hass, UPDATE_INTERVAL, _update)

    async def async_update(self):
        """Manually update the sensor's state (fallback or for total time)."""
        if self._start_time:
            # Calculate current total time including ongoing period
            elapsed = datetime.now() - self._start_time
            current_time = self._total_time + elapsed
        else:
            # Use the accumulated total time
            current_time = self._total_time

        # Format time as hh:mm:ss
        self._state = str(current_time).split(".")[0]
