# custom_components/smart_boiler/const.py

DOMAIN = "smart_boiler"

# Soglie di potenza predefinite (in Watt)
DEFAULT_POWER_THRESHOLD_STANDBY = 50
DEFAULT_POWER_THRESHOLD_ACS = 100
DEFAULT_POWER_THRESHOLD_CIRCULATOR = 150
DEFAULT_POWER_THRESHOLD_HEATING = 200

# Nomi delle nuove entità
SENSOR_HEATING_TIME = "tempo_riscaldamento"
SENSOR_ACS_TIME = "tempo_acs"
SENSOR_TOTAL_TIME = "tempo_totale"

# ID univoci per le entità
ENTITY_ID_BOILER_STATE = f"sensor.{DOMAIN}_boiler_state"
ENTITY_ID_HEATING_TIME = f"sensor.{DOMAIN}_heating_time"
ENTITY_ID_ACS_TIME = f"sensor.{DOMAIN}_acs_time"
ENTITY_ID_TOTAL_TIME = f"sensor.{DOMAIN}_total_time"
