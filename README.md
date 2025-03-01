# Smart Boiler

Integra la tua caldaia intelligente in Home Assistant.

## Funzionalità
- Monitora lo stato della caldaia (accesa/spenta).
- Imposta la temperatura target.
- Fornisce informazioni sull'efficienza energetica.
- Calcola il consumo di gas.

## Installazione
1. Installa [HACS](https://hacs.xyz) se non lo hai già fatto.
2. Aggiungi questo repository in HACS:
   - Vai a **HACS > Integrations > 3 dots (menu) > Custom repositories**.
   - Inserisci l'URL del repository: `https://github.com/tuo-username/smart_boiler`.
   - Seleziona **Integration** come categoria.
3. Clicca su **Install** per installare il componente.
4. Riavvia Home Assistant.

## Configurazione
Aggiungi il seguente codice al tuo `configuration.yaml`:

```yaml
sensor:
  - platform: smart_boiler