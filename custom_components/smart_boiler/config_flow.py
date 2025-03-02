# custom_components/smart_boiler/config_flow.py
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import DOMAIN, GAS_TYPES

class SmartBoilerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Boiler."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Salva le entità selezionate e i parametri della caldaia
            return self.async_create_entry(title="Smart Boiler", data=user_input)

        # Schema per la selezione delle entità e i parametri della caldaia
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
                selector.EntitySelectorConfig(domain="switch")  # Solo entità di tipo switch
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
            vol.Optional("max_heating_water_temp"): vol.Coerce(float),  # Temperatura massima di esercizio acqua riscaldamento
            vol.Optional("max_hot_water_temp"): vol.Coerce(float),  # Temperatura massima di esercizio acqua sanitaria
            vol.Required("standby_power"): vol.Coerce(float),  # Potenza in standby
            vol.Required("hot_water_power"): vol.Coerce(float),  # Potenza produzione acqua calda
            vol.Required("heating_power"): vol.Coerce(float),  # Potenza riscaldamento
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SmartBoilerOptionsFlow(config_entry)

class SmartBoilerOptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow for Smart Boiler."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Aggiorna le entità selezionate e i parametri della caldaia
            return self.async_create_entry(title="", data=user_input)

        # Schema per la selezione delle entità e i parametri della caldaia
        data_schema = vol.Schema({
            vol.Required("external_temp_entity", default=self.config_entry.options.get("external_temp_entity")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
            ),
            vol.Required("flue_temp_entity", default=self.config_entry.options.get("flue_temp_entity")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
            ),
            vol.Required("hot_water_temp_entity", default=self.config_entry.options.get("hot_water_temp_entity")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
            ),
            vol.Required("cold_water_temp_entity", default=self.config_entry.options.get("cold_water_temp_entity")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
            ),
            vol.Required("heating_supply_temp_entity", default=self.config_entry.options.get("heating_supply_temp_entity")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
            ),
            vol.Required("heating_return_temp_entity", default=self.config_entry.options.get("heating_return_temp_entity")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
            ),
            vol.Required("thermostat_demand_entity", default=self.config_entry.options.get("thermostat_demand_entity")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="switch")
            ),
            vol.Required("photoresistor_entity", default=self.config_entry.options.get("photoresistor_entity")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["binary_sensor", "sensor"])
            ),
            vol.Required("electric_consumption_entity", default=self.config_entry.options.get("electric_consumption_entity")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="power")
            ),
            vol.Required("heating_power_nominal_kw", default=self.config_entry.options.get("heating_power_nominal_kw")): vol.Coerce(float),
            vol.Required("hot_water_power_nominal_kw", default=self.config_entry.options.get("hot_water_power_nominal_kw")): vol.Coerce(float),
            vol.Required("gas_type", default=self.config_entry.options.get("gas_type")): vol.In(list(GAS_TYPES.keys())),
            vol.Required("gas_flow_rate", default=self.config_entry.options.get("gas_flow_rate")): vol.Coerce(float),
            vol.Optional("heating_flow_nominal_kw", default=self.config_entry.options.get("heating_flow_nominal_kw")): vol.Coerce(float),
            vol.Optional("adjustable_power_max_kw", default=self.config_entry.options.get("adjustable_power_max_kw")): vol.Coerce(float),
            vol.Optional("water_capacity_dm3", default=self.config_entry.options.get("water_capacity_dm3")): vol.Coerce(float),
            vol.Optional("max_heating_water_temp", default=self.config_entry.options.get("max_heating_water_temp")): vol.Coerce(float),
            vol.Optional("max_hot_water_temp", default=self.config_entry.options.get("max_hot_water_temp")): vol.Coerce(float),
            vol.Required("standby_power", default=self.config_entry.options.get("standby_power")): vol.Coerce(float),
            vol.Required("hot_water_power", default=self.config_entry.options.get("hot_water_power")): vol.Coerce(float),
            vol.Required("heating_power", default=self.config_entry.options.get("heating_power")): vol.Coerce(float),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
