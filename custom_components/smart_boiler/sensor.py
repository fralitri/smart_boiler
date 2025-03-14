class SmartBoilerStateSensor(Entity):
    """Representation of the Smart Boiler State Sensor."""

    def __init__(self, hass, config_entry, unique_id, dhw_outlet_temp, cold_water_inlet_temp, heating_outlet_temp, heating_return_temp, flue_gas_temp, power_entity, threshold_standby, threshold_dhw, threshold_circulator, threshold_heating):
        """Initialize the sensor."""
        self._hass = hass
        self._config_entry = config_entry
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

        # Use translations for the entity name
        self._name = self._hass.config_entries.async_get_entry(config_entry.entry_id).title

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
        elif self._state == "dhw":
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
        """Handle state changes for the power and temperature sensors."""
        await self.async_update()
        self.async_write_ha_state()

    async def async_update(self):
        """Fetch new state data for the sensor."""
        # Fetch temperature states
        dhw_outlet_state = self._hass.states.get(self._dhw_outlet_temp)
        cold_water_inlet_state = self._hass.states.get(self._cold_water_inlet_temp)
        heating_outlet_state = self._hass.states.get(self._heating_outlet_temp)
        heating_return_state = self._hass.states.get(self._heating_return_temp)
        flue_gas_state = self._hass.states.get(self._flue_gas_temp)

        # Fetch power state
        power_state = self._hass.states.get(self._power_entity)

        # Check if any state is invalid
        if any(state is None or state.state in ["unknown", "unavailable"] for state in [dhw_outlet_state, cold_water_inlet_state, heating_outlet_state, heating_return_state, flue_gas_state, power_state]):
            self._state = "error"
            return

        try:
            # Convert temperature states to float
            dhw_outlet_temp = float(dhw_outlet_state.state)
            cold_water_inlet_temp = float(cold_water_inlet_state.state)
            heating_outlet_temp = float(heating_outlet_state.state)
            heating_return_temp = float(heating_return_state.state)
            flue_gas_temp = float(flue_gas_state.state)

            # Convert power state to float
            power = float(power_state.state)
        except (ValueError, TypeError):
            self._state = "error"
            return

        # Determine the boiler state based on power
        if power < self._threshold_standby:
            self._state = "standby"
        elif self._threshold_standby <= power < self._threshold_dhw:
            self._state = "dhw"
        elif self._threshold_dhw <= power < self._threshold_circulator:
            self._state = "circulator"
        elif self._threshold_circulator <= power < self._threshold_heating:
            self._state = "heating"
        else:
            self._state = "error"

        # Update attributes with temperatures and power
        self._attributes = {
            "dhw_outlet_temp": dhw_outlet_temp,
            "cold_water_inlet_temp": cold_water_inlet_temp,
            "heating_outlet_temp": heating_outlet_temp,
            "heating_return_temp": heating_return_temp,
            "flue_gas_temp": flue_gas_temp,
            "power": power,
            "threshold_standby": self._threshold_standby,
            "threshold_dhw": self._threshold_dhw,
            "threshold_circulator": self._threshold_circulator,
            "threshold_heating": self._threshold_heating,
        }
