{
  "config": {
    "step": {
      "user": {
        "title": "Configure Smart Boiler",
        "description": "Set up your Smart Boiler integration.",
        "data": {
          "hot_water_temp_entity": "Hot Water Temperature Sensor",
          "cold_water_temp_entity": "Cold Water Temperature Sensor",
          "heating_supply_temp_entity": "Heating Supply Temperature Sensor",
          "heating_return_temp_entity": "Heating Return Temperature Sensor",
          "flue_temp_entity": "Flue Temperature Sensor",
          "power_entity": "Boiler Power Sensor",
          "power_threshold_standby": "Standby Power Threshold (W)",
          "power_threshold_acs": "ACS Power Threshold (W)",
          "power_threshold_circulator": "Circulator Power Threshold (W)",
          "power_threshold_heating": "Heating Power Threshold (W)"
        }
      }
    },
    "error": {
      "invalid_entity": "Invalid entity selected."
    },
    "abort": {
      "already_configured": "This device is already configured."
    }
  }
}
