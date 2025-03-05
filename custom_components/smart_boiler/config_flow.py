# custom_components/smart_boiler/config_flow.py
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import (
    DOMAIN,
    DEFAULT_POWER_THRESHOLD_STANDBY,
    DEFAULT_POWER_THRESHOLD_ACS,
    DEFAULT_POWER_THRESHOLD_CIRCULATOR,
    DEFAULT_POWER_THRESHOLD_HEATING,
)

class SmartBoilerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Boiler."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="Smart Boiler", data=user_input)

        # Schema per la selezione delle entità e delle soglie
        data_schema = vol.Schema({
            vol.Required("hot_water_temp_entity"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature"),
                description=self.hass.data[DOMAIN]["translations"]["config"]["step"]["user"]["data_description"]["hot_water_temp_entity"]
            ),
            vol.Required("cold_water_temp_entity"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature"),
                description=self.hass.data[DOMAIN]["translations"]["config"]["step"]["user"]["data_description"]["cold_water_temp_entity"]
            ),
            vol.Required("heating_supply_temp_entity"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature"),
                description=self.hass.data[DOMAIN]["translations"]["config"]["step"]["user"]["data_description"]["heating_supply_temp_entity"]
            ),
            vol.Required("heating_return_temp_entity"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature"),
                description=self.hass.data[DOMAIN]["translations"]["config"]["step"]["user"]["data_description"]["heating_return_temp_entity"]
            ),
            vol.Required("flue_temp_entity"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature"),
                description=self.hass.data[DOMAIN]["translations"]["config"]["step"]["user"]["data_description"]["flue_temp_entity"]
            ),
            vol.Required("power_entity"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="power"),
                description=self.hass.data[DOMAIN]["translations"]["config"]["step"]["user"]["data_description"]["power_entity"]
            ),
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
