async def create_time_sensors(hass, config_entry):
    """Crea i sensori di tempo utilizzando HistoryStats e Template Sensor."""
    entities = []

    # Configurazione per i sensori HistoryStats
    history_stats_config = {
        "entity_id": config_entry.data["power_entity"],
        "start": "{{ today_at() }}",
        "end": "{{ now() }}",
        "type": "time",
    }

    # Sensore "Tempo Riscaldamento"
    heating_time_sensor = HistoryStatsSensor(
        hass=hass,
        sensor_type="time",  # Tipo di sensore
        name=SENSOR_HEATING_TIME,  # Nome del sensore
        unique_id=f"{DOMAIN}_{SENSOR_HEATING_TIME}",  # ID univoco
        source_entity_id=config_entry.data["power_entity"],  # Entità sorgente
        **history_stats_config  # Configurazione aggiuntiva
    )
    entities.append(heating_time_sensor)

    # Sensore "Tempo ACS"
    acs_time_sensor = HistoryStatsSensor(
        hass=hass,
        sensor_type="time",
        name=SENSOR_ACS_TIME,
        unique_id=f"{DOMAIN}_{SENSOR_ACS_TIME}",
        source_entity_id=config_entry.data["power_entity"],
        **history_stats_config
    )
    entities.append(acs_time_sensor)

    # Sensore "Tempo Totale"
    total_time_sensor = HistoryStatsSensor(
        hass=hass,
        sensor_type="time",
        name=SENSOR_TOTAL_TIME,
        unique_id=f"{DOMAIN}_{SENSOR_TOTAL_TIME}",
        source_entity_id=config_entry.data["power_entity"],
        **history_stats_config
    )
    entities.append(total_time_sensor)

    # Configurazione per i sensori Template
    template_config = {
        "platform": "template",
        "sensors": {
            "tempo_riscaldamento_formattato": {
                "friendly_name": "Tempo Riscaldamento (hh:mm:ss)",
                "value_template": '{% set hours = states("sensor.tempo_riscaldamento") | float %}'
                                 '{{ "%02d:%02d:%02d" | format(hours // 1, (hours % 1 * 60) // 1, (hours % 1 * 3600) % 60) }}',
                "icon": "mdi:radiator",
                CONF_UNIQUE_ID: f"{DOMAIN}_tempo_riscaldamento_formattato",
            },
            "tempo_acs_formattato": {
                "friendly_name": "Tempo ACS (hh:mm:ss)",
                "value_template": '{% set hours = states("sensor.tempo_acs") | float %}'
                                 '{{ "%02d:%02d:%02d" | format(hours // 1, (hours % 1 * 60) // 1, (hours % 1 * 3600) % 60) }}',
                "icon": "mdi:water-pump",
                CONF_UNIQUE_ID: f"{DOMAIN}_tempo_acs_formattato",
            },
            "tempo_totale_formattato": {
                "friendly_name": "Tempo Totale (hh:mm:ss)",
                "value_template": '{% set hours = states("sensor.tempo_totale") | float %}'
                                 '{{ "%02d:%02d:%02d" | format(hours // 1, (hours % 1 * 60) // 1, (hours % 1 * 3600) % 60) }}',
                "icon": "mdi:clock",
                CONF_UNIQUE_ID: f"{DOMAIN}_tempo_totale_formattato",
            },
        },
    }

    # Aggiungi i sensori template
    for sensor_name, sensor_config in template_config["sensors"].items():
        template_sensor = SensorTemplate(
            hass,
            sensor_config,
            sensor_name,
        )
        entities.append(template_sensor)

    return entities
