### Smart Boiler

Trasforma la tua caldaia in una caldaia intelligente integrata in Home Assistant.

#### Funzionalità

##### Versione 1.0
- Monitora le temperature della caldaia.

##### Versione 2.0
- Aggiunti sensori per il tempo di funzionamento della caldaia:
  - **Tempo di riscaldamento**: Misura il tempo totale in cui la caldaia è in modalità riscaldamento.
  - **Tempo ACS**: Misura il tempo totale in cui la caldaia è in modalità acqua calda sanitaria (ACS).
  - **Tempo totale**: Misura il tempo totale di funzionamento (riscaldamento + ACS).
- Icone dinamiche per lo stato della caldaia.
- Tempi di funzionamento in formato `hh:mm:ss`.
- Azzeramento automatico dei tempi a mezzanotte.
- ID univoci per tutte le entità:
  - `sensor.smart_boiler_boiler_state`
  - `sensor.smart_boiler_heating_time`
  - `sensor.smart_boiler_acs_time`
  - `sensor.smart_boiler_total_time`

#### Requisiti
- Home Assistant 2023.1 o superiore.
- HACS installato.

#### Installazione
1. Aggiungi questo repository in HACS.
2. Clicca su **Install**.
3. Riavvia Home Assistant.
