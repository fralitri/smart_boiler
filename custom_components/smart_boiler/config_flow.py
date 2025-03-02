data_schema = vol.Schema({
    vol.Required("external_temp_entity"): selector.EntitySelector(
        selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
    ),
    vol.Required("flue_temp_entity"): selector.EntitySelector(
        selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
    ),
    vol.Required("hot_water_temp_entity"): selector.EntitySelector(
        selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
    ),
    vol.Required("cold_water_temp_entity"): selector.EntitySelector(
        selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
    ),
    vol.Required("heating_supply_temp_entity"): selector.EntitySelector(
        selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
    ),
    vol.Required("heating_return_temp_entity"): selector.EntitySelector(
        selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
    ),
    vol.Required("thermostat_demand_entity"): selector.EntitySelector(
        selector.EntitySelectorConfig(domain="switch")  # Cambiato a "switch"
    ),
    vol.Required("photoresistor_entity"): selector.EntitySelector(
        selector.EntitySelectorConfig(domain=["binary_sensor", "sensor"])  # Supporta sia switch che valori analogici
    ),
    vol.Required("electric_consumption_entity"): selector.EntitySelector(
        selector.EntitySelectorConfig(domain="sensor", device_class="power")
    ),
    vol.Required("heating_power_nominal_kw"): vol.Coerce(float),
    vol.Required("hot_water_power_nominal_kw"): vol.Coerce(float),
    vol.Required("gas_type"): vol.In(list(GAS_TYPES.keys())),
    vol.Required("gas_flow_rate"): vol.Coerce(float),
    vol.Optional("heating_flow_nominal_kw"): vol.Coerce(float),
    vol.Optional("adjustable_power_max_kw"): vol.Coerce(float),
    vol.Optional("water_capacity_dm3"): vol.Coerce(float),
    vol.Optional("max_heating_water_temp"): vol.Coerce(float),
    vol.Optional("max_hot_water_temp"): vol.Coerce(float),
    vol.Required("standby_power"): vol.Coerce(float),  # Potenza in standby
    vol.Required("hot_water_power"): vol.Coerce(float),  # Potenza produzione acqua calda
    vol.Required("heating_power"): vol.Coerce(float),  # Potenza riscaldamento
})
