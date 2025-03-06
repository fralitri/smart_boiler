# Smart Boiler

Integra la tua caldaia intelligente in Home Assistant.

## Funzionalità

### Versione 1.0
- Monitoraggio delle temperature della caldaia.
- Creazione automatica di una scheda Lovelace per visualizzare i dati.

### Versione 2.0
- Aggiunti sensori per il tempo di funzionamento della caldaia:
  - **Tempo di riscaldamento**: Misura il tempo totale in cui la caldaia è in modalità riscaldamento.
  - **Tempo ACS**: Misura il tempo totale in cui la caldaia è in modalità acqua calda sanitaria (ACS).
  - **Tempo totale**: Misura il tempo totale di funzionamento (riscaldamento + ACS).

## Installazione
1. Installa [HACS](https://hacs.xyz) se non lo hai già fatto.
2. Aggiungi questo repository in HACS:
   - Vai a **HACS > Integrations > 3 dots (menu) > Custom repositories**.
   - Inserisci l'URL del repository: `https://github.com/tuo-username/smart_boiler`.
   - Seleziona **Integration** come categoria.
3. Clicca su **Install** per installare il componente.
4. Riavvia Home Assistant.

## Aggiornamenti
- **Versione 2.0**: Aggiunti sensori per il tempo di funzionamento della caldaia.
- **Versione 1.0**: Funzionalità iniziali di monitoraggio delle temperature.
