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
