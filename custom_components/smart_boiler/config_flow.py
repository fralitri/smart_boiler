# custom_components/smart_boiler/config_flow.py
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import DOMAIN, DEFAULT_POWER_THRESHOLD_STANDBY, DEFAULT_POWER_THRESHOLD_ACS, DEFAULT_POWER_THRESHOLD_CIRCULATOR, DEFAULT_POWER_THRESHOLD_HEATING

_LOGGER = logging.getLogger(__name__)

class SmartBoilerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Boiler."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            _LOGGER.debug(f"Dati inseriti dall'utente: {user_input}")
            try:
                # Verifica che tutti i campi siano presenti
                required_fields = [
                    "hot_water_temp_entity",
                    "cold_water_temp_entity",
                    "heating_supply_temp_entity",
                    "heating_return_temp_entity",
                    "flue_temp_entity",
                    "power_entity",
                    "thermal_power",
                    "gas_type",
                    "power_threshold_standby",
                    "power_threshold_acs",
                    "power_threshold_circulator",
                    "power_threshold_heating",
                ]
                for field in required_fields:
                    if field not in user_input:
                        errors[field] = "campo_obbligatorio"
                        _LOGGER.error(f"Campo mancante: {field}")

                if not errors:
                    _LOGGER.debug("Tutti i campi sono validi. Creazione della configurazione.")
                    return self.async_create_entry(title="Smart Boiler", data=user_input)
            except Exception as e:
                _LOGGER.error(f"Errore durante la configurazione: {e}")
                errors["base"] = "unknown"

        # Schema per la selezione delle entità e delle soglie
        data_schema = vol.Schema({
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
            vol.Required("flue_temp_entity"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
            ),
            vol.Required("power_entity"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="power")
            ),
            vol.Required("thermal_power"): vol.Coerce(float),  # Potenza termica in kW
            vol.Required("gas_type"): vol.In(["metano", "gpl"]),  # Tipo di gas
            vol.Required("power_threshold_standby", default=DEFAULT_POWER_THRESHOLD_STANDBY): int,
            vol.Required("power_threshold_acs", default=DEFAULT_POWER_THRESHOLD_ACS): int,
            vol.Required("power_threshold_circulator", default=DEFAULT_POWER_THRESHOLD_CIRCULATOR): int,
            vol.Required("power_threshold_heating", default=DEFAULT_POWER_THRESHOLD_HEATING): int,
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
            return self.async_create_entry(title="", data=user_input)

        # Schema per la selezione delle entità e delle soglie
        data_schema = vol.Schema({
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
            vol.Required("flue_temp_entity", default=self.config_entry.options.get("flue_temp_entity")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
            ),
            vol.Required("power_entity", default=self.config_entry.options.get("power_entity")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="power")
            ),
            vol.Required("thermal_power", default=self.config_entry.options.get("thermal_power", 24)): vol.Coerce(float),  # Potenza termica in kW
            vol.Required("gas_type", default=self.config_entry.options.get("gas_type", "metano")): vol.In(["metano", "gpl"]),  # Tipo di gas
            vol.Required("power_threshold_standby", default=self.config_entry.options.get("power_threshold_standby", DEFAULT_POWER_THRESHOLD_STANDBY)): int,
            vol.Required("power_threshold_acs", default=self.config_entry.options.get("power_threshold_acs", DEFAULT_POWER_THRESHOLD_ACS)): int,
            vol.Required("power_threshold_circulator", default=self.config_entry.options.get("power_threshold_circulator", DEFAULT_POWER_THRESHOLD_CIRCULATOR)): int,
            vol.Required("power_threshold_heating", default=self.config_entry.options.get("power_threshold_heating", DEFAULT_POWER_THRESHOLD_HEATING)): int,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
