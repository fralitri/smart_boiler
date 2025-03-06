# custom_components/smart_boiler/const.py
DOMAIN = "smart_boiler"

# Soglie di potenza predefinite (in Watt)
DEFAULT_POWER_THRESHOLD_STANDBY = 50
DEFAULT_POWER_THRESHOLD_ACS = 100
DEFAULT_POWER_THRESHOLD_CIRCULATOR = 150
DEFAULT_POWER_THRESHOLD_HEATING = 200

# Nomi delle nuove entità
SENSOR_HEATING_TIME = "smart_boiler_heating_time"
SENSOR_ACS_TIME = "smart_boiler_acs_time"
SENSOR_TOTAL_TIME = "smart_boiler_total_time"
