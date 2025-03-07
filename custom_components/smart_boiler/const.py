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

# Unique ID per le entità
UNIQUE_ID_BOILER_STATE = f"{DOMAIN}_stato_caldaia"
UNIQUE_ID_HEATING_TIME = f"{DOMAIN}_heating_time"
UNIQUE_ID_ACS_TIME = f"{DOMAIN}_acs_time"
UNIQUE_ID_TOTAL_TIME = f"{DOMAIN}_total_time"
