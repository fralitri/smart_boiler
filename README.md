# Smart Boiler

Transform your boiler into a smart boiler integrated with Home Assistant.

## Features

### Version 1.0
- Boiler temperature monitoring.

### Version 2.0
- Added sensors for boiler operation time:
  - **Heating Time**: Measures the total time the boiler has been in heating mode.
  - **ACS Time**: Measures the total time the boiler has been in domestic hot water (ACS) mode.
  - **Total Time**: Measures the total operation time (heating + ACS).
- Dynamic icons for boiler state.
- Operation times in `hh:mm:ss` format.
- Automatic reset of times at midnight.

## Installation
1. Install [HACS](https://hacs.xyz) if you haven't already.
2. Add this repository to HACS:
   - Go to **HACS > Integrations > 3 dots (menu) > Custom repositories**.
   - Enter the repository URL: `https://github.com/your-username/smart_boiler`.
   - Select **Integration** as the category.
3. Click on **Install** to install the component.
4. Restart Home Assistant.

## Updates
- **Version 2.0**: Added sensors for boiler operation time, dynamic icons, and `hh:mm:ss` format.
- **Version 1.0**: Initial boiler temperature monitoring features.

## Usage Instructions
- **Boiler State**: Displays the current state of the boiler (heating, ACS, standby, circulator, error).
- **Heating Time**: Shows the total time the boiler has been in heating mode
