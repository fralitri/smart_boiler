# custom_components/smart_boiler/sensor.py
import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.const import UnitOfPower, UnitOfVolume

_LOGGER = logging.getLogger(__name__)

# Fattori di conversione per il gas (kWh per unità di gas)
GAS_CONVERSION_FACTORS = {
    "metano": 10,  # 1 m³ di metano ≈ 10 kWh
    "gpl": 13,     # 1 kg di GPL ≈ 13 kWh
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smart Boiler sensors from a config entry."""
    entities = []

    # Debug: Stampa le configurazioni
    _LOGGER.debug(f"Configurazioni: {config_entry.data}")

    # Crea il sensore "Stato Caldaia"
    boiler_state_sensor = SmartBoilerStateSensor(
        hass,
        "Stato Caldaia",
        config_entry.data["power_entity"],
        config_entry.data["power_threshold_standby"],
        config_entry.data["power_threshold_acs"],
        config_entry.data["power_threshold_circulator"],
        config_entry.data["power_threshold_heating"],
    )

    # Crea i sensori per il consumo di gas
    gas_consumption_acs = GasConsumptionSensor(
        hass,
        "Consumo GAS Acqua Sanitaria",
        boiler_state_sensor,
        "acs",
        config_entry.data["thermal_power"],
        config_entry.data["gas_type"],
    )

    gas_consumption_heating = GasConsumptionSensor(
        hass,
        "Consumo GAS Riscaldamento",
        boiler_state_sensor,
        "riscaldamento",
        config_entry.data["thermal_power"],
        config_entry.data["gas_type"],
    )

    gas_consumption_total = GasConsumptionSensor(
        hass,
        "Consumo GAS Caldaia",
        boiler_state_sensor,
        None,  # Somma di tutti i consumi
        config_entry.data["thermal_power"],
        config_entry.data["gas_type"],
    )

    # Aggiungi i sensori alla lista delle entità
    entities.extend([
        boiler_state_sensor,
        gas_consumption_acs,
        gas_consumption_heating,
        gas_consumption_total,
    ])

    # Debug: Stampa le entità create
    _LOGGER.debug(f"Entità create: {entities}")

    # Registra le entità in Home Assistant
    async_add_entities(entities, update_before_add=True)

    # Aggiungi un listener per aggiornamenti in tempo reale
    async_track_state_change(
        hass, config_entry.data["power_entity"], boiler_state_sensor.async_update_callback
    )

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

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return self._attributes

    async def async_update_callback(self, entity_id, old_state, new_state):
        """Handle state changes for the power sensor."""
        await self.async_update()
        self.async_write_ha_state()  # Aggiorna lo stato in Home Assistant

    async def async_update(self):
        """Fetch new state data for the sensor."""
        power_state = self._hass.states.get(self._power_entity)
        if power_state is None or power_state.state in ["unknown", "unavailable"]:
            self._state = "errore"
            return

        try:
            power = float(power_state.state)
        except (ValueError, TypeError):
            self._state = "errore"
            return

        # Determina lo stato della caldaia
        if power < self._threshold_standby:
            self._state = "standby"
        elif self._threshold_standby <= power < self._threshold_acs:
            self._state = "acs"
        elif self._threshold_acs <= power < self._threshold_circulator:
            self._state = "circolatore"
        elif self._threshold_circulator <= power < self._threshold_heating:
            self._state = "riscaldamento"
        else:
            self._state = "errore"

        # Aggiorna gli attributi
        self._attributes = {
            "power": power,
            "threshold_standby": self._threshold_standby,
            "threshold_acs": self._threshold_acs,
            "threshold_circulator": self._threshold_circulator,
            "threshold_heating": self._threshold_heating,
        }

class GasConsumptionSensor(Entity):
    """Representation of a Gas Consumption Sensor."""

    def __init__(self, hass, name, boiler_state_sensor, mode, thermal_power, gas_type):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._boiler_state_sensor = boiler_state_sensor
        self._mode = mode  # "acs", "riscaldamento", o None (totale)
        self._thermal_power = thermal_power  # Potenza termica in kW
        self._gas_type = gas_type  # Tipo di gas (metano, GPL)
        self._state = 0.0  # Consumo cumulativo in m³ o kg
        self._last_update = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return UnitOfVolume.CUBIC_METERS if self._gas_type == "metano" else "kg"

    async def async_update(self):
        """Update the gas consumption based on the boiler state."""
        now = self._hass.states.get("sensor.date_time").state
        if self._last_update is None:
            self._last_update = now
            return

        # Calcola il tempo trascorso dall'ultimo aggiornamento
        time_elapsed = (now - self._last_update).total_seconds() / 3600  # in ore

        # Ottieni lo stato della caldaia
        boiler_state = self._boiler_state_sensor.state

        # Calcola il consumo di gas solo se lo stato corrisponde alla modalità
        if self._mode is None or boiler_state == self._mode:
            gas_consumption = self._thermal_power * time_elapsed / GAS_CONVERSION_FACTORS[self._gas_type]
            self._state += gas_consumption

        # Aggiorna l'ultimo timestamp
        self._last_update = now

    async def async_update_callback(self, entity_id, old_state, new_state):
        """Handle state changes for the boiler state sensor."""
        await self.async_update()
        self.async_write_ha_state()  # Aggiorna lo stato in Home Assistant
