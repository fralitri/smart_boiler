# custom_components/smart_boiler/sensor.py

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
        self._unique_id = f"{DOMAIN}_{name.lower().replace(' ', '_')}"  # Aggiungi un ID univoco

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    # Resto del codice rimane invariato...

class SmartBoilerTimeSensor(Entity):
    """Representation of a Smart Boiler Time Sensor."""

    def __init__(self, hass, name, target_states, icon):
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
        self._unique_id = f"{DOMAIN}_{name.lower().replace(' ', '_')}"  # Aggiungi un ID univoco

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    # Resto del codice rimane invariato...
