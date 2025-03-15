# Smart Boiler

Transform your boiler into a smart boiler integrated with Home Assistant.

## Features

### Version 1.00.00
- Monitor boiler temperatures.
- Monitor electrical consumption to determine the boiler's operating state:
  - **Standby**: Boiler is in standby mode.
  - **ACS**: Boiler is in domestic hot water mode.
  - **Circulator**: Boiler is in circulator mode.
  - **Heating**: Boiler is in heating mode.

### Version 1.01.00
- Added sensors to measure the time spent in specific boiler states:
  - **Heating Time**: Measures the total time the boiler has been in heating mode.
  - **ACS Time**: Measures the total time the boiler has been in domestic hot water mode.
  - **Total Time**: Measures the total operating time (heating + ACS).
- Dynamic icons for boiler states.
- Operating times in `hh:mm:ss` format.
- Automatic reset of times at midnight.

## Installation
1. Install [HACS](https://hacs.xyz) if you haven't already.
2. Add this repository to HACS:
   - Go to **HACS > Integrations > 3 dots (menu) > Custom repositories**.
   - Enter the repository URL: `https://github.com/fralitri/smart_boiler`.
   - Select **Integration** as the category.
3. Click **Install** to install the component.
4. Restart Home Assistant.

## Updates
- **Version 1.01.00**: Added sensors to measure time spent in ACS and heating modes, dynamic icons, and `hh:mm:ss` format.
- **Version 1.00.00**: Initial features for monitoring boiler temperatures and electrical consumption.

## Usage
- **Boiler State**: Displays the current state of the boiler (heating, ACS, standby, circulator, error).
- **Heating Time**: Shows the total time the boiler has been in heating mode.
- **ACS Time**: Shows the total time the boiler has been in domestic hot water mode.
- **Total Time**: Shows the total operating time (heating + ACS).

Operating times are automatically reset every day at midnight.
