# Smart Boiler

Transform your boiler into a smart boiler integrated with Home Assistant.

## Features

### Version 1.0.0
- Monitor boiler temperatures.
- Monitor boiler electrical power consumption.
- Determine the boiler state based on power consumption:
  - **Standby**: When power consumption is below the standby threshold.
  - **Domestic Hot Water (DHW)**: When power consumption is between the standby and DHW thresholds.
  - **Circulator**: When power consumption is between the DHW and circulator thresholds.
  - **Heating**: When power consumption is between the circulator and heating thresholds.

## Installation
1. Install [HACS](https://hacs.xyz) if you haven't already.
2. Add this repository to HACS:
   - Go to **HACS > Integrations > 3 dots (menu) > Custom repositories**.
   - Enter the repository URL: `https://github.com/fralitri/smart_boiler`.
   - Select **Integration** as the category.
3. Click **Install** to install the component.
4. Restart Home Assistant.

## Usage Instructions
- **Boiler Status**: Displays the current status of the boiler (standby, DHW, circulator, heating, or error).
- **Power Consumption**: Monitors the boiler's electrical power consumption.
- **Temperature Monitoring**: Tracks the boiler's temperatures.

For more information, visit the [GitHub repository](https://github.com/fralitri/smart_boiler).
