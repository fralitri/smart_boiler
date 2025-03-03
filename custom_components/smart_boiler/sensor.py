async def async_update(self):
    """Fetch new state data for the sensor."""
    power_state = self.hass.states.get(self._power_entity)
    if power_state is None or power_state.state in ["unknown", "unavailable"]:
        _LOGGER.warning(f"Sensore di potenza {self._power_entity} non valido: {power_state.state}")
        self._state = "errore"
        return

    try:
        power = float(power_state.state)
    except (ValueError, TypeError):
        _LOGGER.warning(f"Valore di potenza non valido: {power_state.state}")
        self._state = "errore"
        return

    # Debug: Stampa i valori di potenza e soglie
    _LOGGER.debug(f"Potenza: {power} W, Soglie: standby={self._threshold_standby}, acs={self._threshold_acs}, circolatore={self._threshold_circulator}, riscaldamento={self._threshold_heating}")

    # Determina lo stato della caldaia
    if power < self._threshold_standby:
        self._state = "standby"
    elif self._threshold_standby <= power < self._threshold_acs:
        self._state = "acs"
    elif self._threshold_acs <= power < self._threshold_circulator:
        self._state = "circolatore"
        _LOGGER.debug(f"Stato Caldaia determinato: circolatore (potenza={power} W)")
    elif self._threshold_circulator <= power < self._threshold_heating:
        self._state = "riscaldamento"
    else:
        self._state = "errore"

    # Debug: Stampa lo stato determinato
    _LOGGER.debug(f"Stato Caldaia determinato: {self._state}")

    # Aggiorna gli attributi
    self._attributes = {
        "power": power,
        "threshold_standby": self._threshold_standby,
        "threshold_acs": self._threshold_acs,
        "threshold_circulator": self._threshold_circulator,
        "threshold_heating": self._threshold_heating,
    }
