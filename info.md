### Smart Boiler

Transform your boiler into a smart boiler integrated with Home Assistant.

#### Features

##### Version 1.0.0
- Monitor boiler temperatures.
- Monitor boiler electrical power consumption.
- Determine the boiler state based on power consumption:
  - **Standby**: When power consumption is below the standby threshold.
  - **Domestic Hot Water (DHW)**: When power consumption is between the standby and DHW thresholds.
  - **Circulator**: When power consumption is between the DHW and circulator thresholds.
  - **Heating**: When power consumption is between the circulator and heating thresholds.

#### Requirements
- Home Assistant 2023.1 or higher.
- HACS installed.

#### Installation
1. Add this repository to HACS.
2. Click **Install**.
3. Restart Home Assistant.

For more information, visit the [GitHub repository](https://github.com/fralitri/smart_boiler).
