# Smart Boiler

Trasforma la tua caldaia in una caldaia intelligente integrata in Home Assistant.

## Funzionalità

### Versione 1.01.00
- Monitoraggio delle temperature della caldaia.

### Versione 1.02.00
- Aggiunti sensori per il tempo di funzionamento della caldaia:
  - **Tempo di riscaldamento**: Misura il tempo totale in cui la caldaia è in modalità riscaldamento.
  - **Tempo ACS**: Misura il tempo totale in cui la caldaia è in modalità acqua calda sanitaria (ACS).
  - **Tempo totale**: Misura il tempo totale di funzionamento (riscaldamento + ACS).
- Icone dinamiche per lo stato della caldaia.
- Tempi di funzionamento in formato `hh:mm:ss`.
- Azzeramento automatico dei tempi a mezzanotte.

## Installazione
1. Installa [HACS](https://hacs.xyz) se non lo hai già fatto.
2. Aggiungi questo repository in HACS:
   - Vai a **HACS > Integrations > 3 dots (menu) > Custom repositories**.
   - Inserisci l'URL del repository: `https://github.com/tuo-username/smart_boiler`.
   - Seleziona **Integration** come categoria.
3. Clicca su **Install** per installare il componente.
4. Riavvia Home Assistant.

## Aggiornamenti
- **Versione 1.02.00**: Aggiunti sensori per il tempo di funzionamento della caldaia, icone dinamiche e formato `hh:mm:ss`.
- **Versione 1.01.00**: Funzionalità iniziali di monitoraggio delle temperature.

## Istruzioni di funzionamento
- **Stato Caldaia**: Visualizza lo stato attuale della caldaia (riscaldamento, ACS, standby, circolatore, errore).
- **Tempo Riscaldamento**: Mostra il tempo totale in cui la caldaia è stata in modalità riscaldamento.
- **Tempo ACS**: Mostra il tempo totale in cui la caldaia è stata in modalità acqua calda sanitaria.
- **Tempo Totale**: Mostra il tempo totale di funzionamento (riscaldamento + ACS).

I tempi di funzionamento vengono azzerati automaticamente ogni giorno alle 00:00.
