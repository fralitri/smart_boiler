# Smart Boiler

Integration for Home Assistant that monitors the state of a smart boiler based on power consumption.

## Features
- Automatic detection of boiler state (standby, ACS, circulator, heating, error).
- Customizable power thresholds for each state.
- Creation of a sensor entity to monitor the boiler state.

## Installation
1. Add this integration via HACS or manually copy the `smart_boiler` folder to the `custom_components` directory in Home Assistant.
2. Restart Home Assistant.
3. Go to **Settings** > **Devices & Services** > **Add Integration** and search for **Smart Boiler**.
4. Follow the instructions to configure the integration.

## Configuration
During setup, you will need to select:
- A power sensor to monitor the boiler's power consumption.
- Power thresholds for each state (standby, ACS, circulator, heating).

## Support
For issues or support requests, please open an issue on [GitHub](https://github.com/fralitri/smart_boiler).

## License
This project is released under the MIT License. See the [LICENSE](LICENSE) file for more details.
