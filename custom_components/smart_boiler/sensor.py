import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    # Create the main boiler state sensor
    unique_id = f"{config_entry.entry_id}_boiler_state"
    boiler_state_sensor = SmartBoilerStateSensor(
        hass,
        "Boiler State",  # Entity name
        unique_id,
        config_entry.data["power_entity"],
        config_entry.data["power_threshold_standby"],
        config_entry.data["power_threshold_acs"],
        config_entry.data["power_threshold_circulator"],
        config_entry.data["power_threshold_heating"],
    )

    # Create the 5 temperature sensors
    temperature_sensors = []
    for i in range(1, 6):
        unique_id_temperature = f"{config_entry.entry_id}_temperature_{i}"
        temperature_sensor = SmartBoilerTemperatureSensor(
            hass,
            f"Boiler Temperature {i}",  # Entity name
            unique_id_temperature,
            config_entry.data[f"temperature_entity_{i}"],
        )
        temperature_sensors.append(temperature_sensor)

    # Create new sensors for ACS time, heating time, and total time
    unique_id_acs_time = f"{config_entry.entry_id}_acs_time"
    unique_id_heating_time = f"{config_entry.entry_id}_heating_time"
    unique_id_total_time = f"{config_entry.entry_id}_total_time"

    acs_time_sensor = SmartBoilerACSTimeSensor(
        hass,
        "ACS Time",
        unique_id_acs_time,
        config_entry.data["power_entity"],
        config_entry.data["power_threshold_acs"],
    )

    heating_time_sensor = SmartBoilerHeatingTimeSensor(
        hass,
        "Heating Time",
        unique_id_heating_time,
        config_entry.data["power_entity"],
        config_entry.data["power_threshold_heating"],
    )

    total_time_sensor = SmartBoilerTotalTimeSensor(
        hass,
        "Total Time",
        unique_id_total_time,
        unique_id_acs_time,
        unique_id_heating_time,
    )

    # Add all sensors to the list of entities
    async_add_entities(
        [boiler_state_sensor, *temperature_sensors, acs_time_sensor, heating_time_sensor, total_time_sensor],
        update_before_add=True,
    )

    # Add a listener for real-time updates on the power entity
    async_track_state_change(
        hass, config_entry.data["power_entity"], boiler_state_sensor.async_update_callback
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

        # Update attributes
        self._attributes = {
            "power": power,
            "threshold_standby": self._threshold_standby,
            "threshold_acs": self._threshold_acs,
            "threshold_circulator": self._threshold_circulator,
            "threshold_heating": self._threshold_heating,
        }

class SmartBoilerTemperatureSensor(Entity):
    """Representation of a Smart Boiler Temperature Sensor."""

    def __init__(self, hass, name, unique_id, temperature_entity):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._unique_id = unique_id
        self._temperature_entity = temperature_entity
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
        """Return the icon of the sensor."""
        return "mdi:thermometer"

    async def async_update(self):
        """Fetch new state data for the sensor."""
        temperature_state = self._hass.states.get(self._temperature_entity)
        if temperature_state is None or temperature_state.state in ["unknown", "unavailable"]:
            self._state = None
            return

        try:
            self._state = float(temperature_state.state)
        except (ValueError, TypeError):
            self._state = None

class SmartBoilerACSTimeSensor(Entity):
    """Representation of the Smart Boiler ACS Time Sensor."""

    def __init__(self, hass, name, unique_id, power_entity, threshold_acs):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._unique_id = unique_id
        self._power_entity = power_entity
        self._threshold_acs = threshold_acs
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
        """Return the icon of the sensor."""
        return "mdi:water-pump"

    async def async_update(self):
        """Fetch new state data for the sensor."""
        power_state = self._hass.states.get(self._power_entity)
        if power_state is None or power_state.state in ["unknown", "unavailable"]:
            self._state = None
            return

        try:
            power = float(power_state.state)
        except (ValueError, TypeError):
            self._state = None
            return

        if power >= self._threshold_acs:
            self._state = "on"
        else:
            self._state = "off"

class SmartBoilerHeatingTimeSensor(Entity):
    """Representation of the Smart Boiler Heating Time Sensor."""

    def __init__(self, hass, name, unique_id, power_entity, threshold_heating):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._unique_id = unique_id
        self._power_entity = power_entity
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
        """Return the icon of the sensor."""
        return "mdi:radiator"

    async def async_update(self):
        """Fetch new state data for the sensor."""
        power_state = self._hass.states.get(self._power_entity)
        if power_state is None or power_state.state in ["unknown", "unavailable"]:
            self._state = None
            return

        try:
            power = float(power_state.state)
        except (ValueError, TypeError):
            self._state = None
            return

        if power >= self._threshold_heating:
            self._state = "on"
        else:
            self._state = "off"

class SmartBoilerTotalTimeSensor(Entity):
    """Representation of the Smart Boiler Total Time Sensor."""

    def __init__(self, hass, name, unique_id, acs_sensor, heating_sensor):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._unique_id = unique_id
        self._acs_sensor = acs_sensor
        self._heating_sensor = heating_sensor
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
        """Return the icon of the sensor."""
        return "mdi:clock"

    async def async_update(self):
        """Fetch new state data for the sensor."""
        acs_state = self._hass.states.get(self._acs_sensor)
        heating_state = self._hass.states.get(self._heating_sensor)

        if acs_state is None or heating_state is None:
            self._state = None
            return

        try:
            acs_time = float(acs_state.state)
            heating_time = float(heating_state.state)
            self._state = acs_time + heating_time
        except (ValueError, TypeError):
            self._state = None
