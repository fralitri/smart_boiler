# custom_components/smart_boiler/const.py
DOMAIN = "smart_boiler"

# Default power thresholds (in Watts)
DEFAULT_POWER_THRESHOLD_STANDBY = 20
DEFAULT_POWER_THRESHOLD_ACS = 60
DEFAULT_POWER_THRESHOLD_CIRCULATOR = 100
DEFAULT_POWER_THRESHOLD_HEATING = 140

# Names of the new entities
SENSOR_HEATING_TIME = "heating_time"
SENSOR_ACS_TIME = "acs_time"
SENSOR_TOTAL_TIME = "total_time"
