### Smart Boiler

Transform your boiler into a smart boiler integrated with Home Assistant.

#### Features

##### Version 1.00.00
- Monitor boiler temperatures.
- Monitor electrical consumption to determine the boiler's operating state:
  - **Standby**: Boiler is in standby mode.
  - **ACS**: Boiler is in domestic hot water mode.
  - **Circulator**: Boiler is in circulator mode.
  - **Heating**: Boiler is in heating mode.

##### Version 1.01.00
- Added sensors to measure the time spent in specific boiler states:
  - **Heating Time**: Measures the total time the boiler has been in heating mode.
  - **ACS Time**: Measures the total time the boiler has been in domestic hot water mode.
  - **Total Time**: Measures the total operating time (heating + ACS).
- Dynamic icons for boiler states.
- Operating times in `hh:mm:ss` format.
- Automatic reset of times at midnight.

#### Requirements
- Home Assistant 2023.1 or higher.
- HACS installed.

#### Installation
1. Add this repository to HACS.
2. Click **Install**.
3. Restart Home Assistant.
