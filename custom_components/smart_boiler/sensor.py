# custom_components/smart_boiler/sensor.py
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

    # Filtra i transitori
    if self._state is not None:
        if self._state == "standby" and power < self._threshold_standby:
            return
        elif self._state == "acs" and self._threshold_standby <= power < self._threshold_acs:
            return
        elif self._state == "circolatore" and self._threshold_acs <= power < self._threshold_circulator:
            return
        elif self._state == "riscaldamento" and self._threshold_circulator <= power < self._threshold_heating:
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
