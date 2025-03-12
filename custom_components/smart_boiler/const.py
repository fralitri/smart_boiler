# custom_components/smart_boiler/config_flow.py
data_schema = vol.Schema({
    vol.Required("power_entity"): selector.EntitySelector(
        selector.EntitySelectorConfig(domain="sensor", device_class="power")
    ),
    vol.Required("power_threshold_standby", default=20): int,
    vol.Required("power_threshold_acs", default=60): int,
    vol.Required("power_threshold_circulator", default=100): int,
    vol.Required("power_threshold_heating", default=140): int,
})
