### Smart Boiler

Transform your boiler into a smart boiler integrated with Home Assistant.

#### Features

##### Version 1.0
- Monitor boiler temperatures.

##### Version 2.0
- Added sensors for boiler operation time:
  - **Heating Time**: Measures the total time the boiler has been in heating mode.
  - **ACS Time**: Measures the total time the boiler has been in domestic hot water (ACS) mode.
  - **Total Time**: Measures the total operation time (heating + ACS).
- Dynamic icons for boiler state.
- Operation times in `hh:mm:ss` format.
- Automatic reset of times at midnight.

#### Requirements
- Home Assistant 2023.1 or higher.
- HACS installed.

#### Installation
1. Add this repository to HACS.
2. Click on **Install**.
3. Restart Home Assistant.
