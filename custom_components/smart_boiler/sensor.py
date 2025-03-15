# custom_components/smart_boiler/sensor.py
class SmartBoilerStateSensor(Entity):
    """Representation of the Smart Boiler State Sensor."""

    def __init__(self, hass, config_entry, unique_id, dhw_outlet_temp, cold_water_inlet_temp, heating_outlet_temp, heating_return_temp, flue_gas_temp, power_entity, threshold_standby, threshold_dhw, threshold_circulator, threshold_heating):
        """Initialize the sensor."""
        self._hass = hass
        self._config_entry = config_entry
        self._name = "Boiler State"
        self._unique_id = unique_id
        self._dhw_outlet_temp = dhw_outlet_temp
        self._cold_water_inlet_temp = cold_water_inlet_temp
        self._heating_outlet_temp = heating_outlet_temp
        self._heating_return_temp = heating_return_temp
        self._flue_gas_temp = flue_gas_temp
        self._power_entity = power_entity
        self._threshold_standby = threshold_standby
        self._threshold_dhw = threshold_dhw
        self._threshold_circulator = threshold_circulator
        self._threshold_heating = threshold_heating
        self._state = None
        self._attributes = {}

    # ... (rest of the code remains the same)
