# Changelog

## 1.2.7

- Read multi-relay Tasmota `POWER1` and `POWER2` values from STATE messages.
- Subscribe to `stat/<topic>/POWER1` so thermostat ON/OFF remains available after adding the second relay.

## 1.2.6

- Added a heating binary sensor based on Tasmota `POWER2` (Tuya DP102), independent of thermostat power `POWER1`.
- Documented the required `TuyaMCU 12,102` mapping and MQTT status topic.

## 1.2.5

- Subscribe to Tasmota STATE messages to update thermostat power state.

## 1.2.4

- Fixed setting thermostat presets from Home Assistant.
- Updated device state when Tasmota reports power and Tuya values in RESULT messages.

## 1.2.3

- Updated the HACS logo artwork and README presentation.

## 1.2.2

- Added Material Design Icons for thermostat preset modes.
- Manual mode: `mdi:hand-pointing-right`
- Auto mode: `mdi:auto-fix`
- Away mode: `mdi:exit-run`
- Override mode: `mdi:flash`
- Implements `preset_mode_icon` property for improved UI representation.

## 1.2.1

- Updated Tasmota configuration Backlog command with complete setup including Module 54, Timezone, and NTP servers.
- Added Module 54 (TYWE3S) device configuration.
- Added Timezone 99 (UTC) and NTP server configuration for accurate time synchronization.
- Documented device restart procedure to apply all configuration changes.

## 1.2.0

- Updated Tasmota setup documentation with complete TuyaMCU configuration Backlog command.
- Added TuyaMCU datapoint mappings for optimal device configuration.
- Changed TelePeriod from 300 to 30 seconds for faster telemetry updates.
- Documented temperature resolution setting (`TempRes 1`).

## 1.1.1

- Added local integration artwork for the HY02B05/Floureon thermostat.
- Added Home Assistant thermostat icon metadata to the climate entity.
- Displayed the integration logo in the README.

## 1.1.0

- Added a Home Assistant switch entity for the thermostat child lock.
- Changed child lock writes to use Tuya boolean command `TuyaSend1`.
- Updated documentation with child lock switch topics and examples.

## 1.0.1

- Added HACS-focused README documentation for installation, setup, and support.
- Documented the Tasmota MQTT topics used by the integration.
- Documented the HY02B05/Floureon TuyaMCU datapoint mapping.
- Added Home Assistant setup, flashing notes, and MQTT command examples.
- Aligned the integration manifest version with the patch release.
