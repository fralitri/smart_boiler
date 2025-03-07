# custom_components/smart_boiler/const.py
DOMAIN = "smart_boiler"

# Default power thresholds (in Watts)
DEFAULT_POWER_THRESHOLD_STANDBY = 50
DEFAULT_POWER_THRESHOLD_ACS = 100
DEFAULT_POWER_THRESHOLD_CIRCULATOR = 150
DEFAULT_POWER_THRESHOLD_HEATING = 200

# Names of the new entities
SENSOR_HEATING_TIME = "heating_time"
SENSOR_ACS_TIME = "acs_time"
SENSOR_TOTAL_TIME = "total_time"
