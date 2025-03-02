# custom_components/smart_boiler/config_flow.py
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import DOMAIN

class SmartBoilerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Boiler."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Salva le entità selezionate
            await self.async_create_lovelace_dashboard(user_input)
            return self.async_create_entry(title="Smart Boiler", data=user_input)

        # Schema per la selezione delle entità
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
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_create_lovelace_dashboard(self, user_input):
        """Create a Lovelace dashboard for the Smart Boiler."""
        dashboard_config = {
            "title": "Smart Boiler",
            "views": [
                {
                    "title": "Stato Caldaia",
                    "path": "caldaia",
                    "cards": [
                        {
                            "type": "entities",
                            "title": "Stato Caldaia",
                            "entities": [
                                {"entity": user_input["hot_water_temp_entity"], "name": "Acqua Calda Sanitaria"},
                                {"entity": user_input["cold_water_temp_entity"], "name": "Acqua Fredda Sanitaria"},
                                {"entity": user_input["heating_supply_temp_entity"], "name": "Mandata Riscaldamento"},
                                {"entity": user_input["heating_return_temp_entity"], "name": "Ritorno Riscaldamento"},
                                {"entity": user_input["flue_temp_entity"], "name": "Fumi Caldaia"},
                            ],
                        }
                    ],
                }
            ],
        }

        # Aggiungi la scheda alla dashboard
        await self.hass.services.async_call(
            "lovelace",
            "create",
            {"config": dashboard_config},
        )

        # Notifica di conferma
        await self.hass.services.async_call(
            "notify",
            "persistent_notification",
            {"message": "Scheda Caldaia creata con successo!"},
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

        # Schema per la selezione delle entità
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
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )