# HY02B05 Thermostat for Home Assistant

Custom Home Assistant integration for HY02B05 TuyaMCU thermostats flashed with
Tasmota, including models sold under the Floureon name.

The integration creates a local MQTT climate entity for a Tasmota-powered
thermostat. It listens to Tasmota telemetry, reads the Tuya datapoints reported
by the thermostat MCU, and sends Tuya commands back through Tasmota.

## What It Does

- Adds one Home Assistant `climate` entity for the thermostat.
- Adds one Home Assistant `switch` entity for the child lock.
- Shows current room temperature from Tasmota `TuyaSNS.Temperature`.
- Shows and controls the target temperature from `TuyaSNS.TempSet`.
- Turns heating power on and off through `cmnd/<topic>/POWER`.
- Supports the thermostat operating presets `manual`, `auto`, `away`, and
  `override`.
- Tracks child lock state as a climate entity attribute.
- Uses local MQTT push updates; there is no cloud account and no polling loop.

This integration does not flash the thermostat and does not replace Tasmota. The
device must already be running Tasmota and publishing the expected TuyaMCU MQTT
messages.

## Supported Hardware

Known target devices are HY02B05-style Wi-Fi thermostats that use a Tuya MCU and
an ESP8266/TYWE3S Wi-Fi module. These thermostats are commonly sold as:

- HY02B05
- Floureon HY02B05
- Similar Tuya wall thermostats exposing the same datapoints

The datapoint mapping used by this integration is:

| Datapoint | Meaning | Direction |
| --- | --- | --- |
| DP1 | Power / relay | read and write through Tasmota `POWER` |
| DP2 | Target temperature, tenths of a degree Celsius | write with `TuyaSend2` |
| DP3 | Current room temperature | read from `TuyaSNS.Temperature` |
| DP4 | Operating mode | read and write with `TuyaSend4` |
| DP6 | Child lock | read from `TuyaReceived`, write with `TuyaSend1` |

See [docs/Mapping.md](docs/Mapping.md) for the full MQTT and datapoint notes.

## Requirements

- Home Assistant 2025.6.0 or newer.
- The Home Assistant MQTT integration configured and connected to the same broker
  as Tasmota.
- A HY02B05/Floureon thermostat already flashed with Tasmota.
- Tasmota configured with a unique MQTT topic and the default full topic pattern:
  `%prefix%/%topic%/`.
- Tasmota TuyaMCU reporting enabled so `TuyaReceived` messages are published.

## Install With HACS

This repository is structured as a HACS custom integration:

```text
custom_components/hy02b05/
hacs.json
README.md
```

1. In Home Assistant, open HACS.
2. Open the HACS menu and choose custom repositories.
3. Add this repository URL and select category `Integration`.
4. Download `HY02B05 Thermostat`.
5. Restart Home Assistant.
6. Go to Settings -> Devices & services -> Add integration.
7. Search for `HY02B05 Thermostat`.
8. Enter a friendly name and the Tasmota MQTT topic.

The topic is the Tasmota `%topic%`, not the full MQTT topic. For example, if
Tasmota publishes `tele/Therm_UG_Bureau/SENSOR`, enter:

```text
Therm_UG_Bureau
```

## Manual Install

Copy `custom_components/hy02b05` into your Home Assistant `custom_components`
directory:

```text
config/custom_components/hy02b05/
```

Restart Home Assistant, then add the integration from the UI.

## Tasmota Setup

Configure MQTT in Tasmota with a unique topic. The integration expects these
topics:

```text
tele/<topic>/SENSOR
tele/<topic>/RESULT
stat/<topic>/POWER
cmnd/<topic>/POWER
cmnd/<topic>/TuyaSend2
cmnd/<topic>/TuyaSend1
cmnd/<topic>/TuyaSend4
```

Recommended Tasmota console commands:

```text
SetOption66 1
TelePeriod 300
```

`SetOption66 1` publishes decoded `TuyaReceived` data. See
[docs/Tasmota.md](docs/Tasmota.md) for setup and verification examples.

## Home Assistant Entities

Current release:

| Entity | Description |
| --- | --- |
| `climate.<name>` | Thermostat power, current temperature, target temperature, and preset mode |
| `switch.<name>_child_lock` | Enables or disables the thermostat child lock |

The climate entity supports:

- HVAC modes: `off`, `heat`
- Target temperature: 5 to 35 degrees Celsius, step 0.5
- Presets: `manual`, `auto`, `away`, `override`
- Attribute: `child_lock_enabled`

The child lock switch mirrors DP6 and sends `TuyaSend1 6,1` or `TuyaSend1 6,0`
through Tasmota.

## Troubleshooting

### The Entity Is Unavailable

Check that Home Assistant receives MQTT messages from Tasmota:

```text
tele/<topic>/SENSOR
stat/<topic>/POWER
tele/<topic>/RESULT
```

The entity becomes available after the integration receives a recognized sensor,
power, or Tuya result message.

### Current or Target Temperature Is Missing

Inspect the Tasmota `SENSOR` payload. The integration expects:

```json
{
  "TuyaSNS": {
    "Temperature": 20.5,
    "TempSet": 21.0
  }
}
```

### Preset Mode Does Not Update

Verify that `tele/<topic>/RESULT` contains a `TuyaReceived` payload with
`DpType4Id4`.

### Commands Do Not Work

Use an MQTT client or the Tasmota console to verify that commands reach the
device:

```text
cmnd/<topic>/POWER ON
cmnd/<topic>/TuyaSend2 2,210
cmnd/<topic>/TuyaSend4 4,0
cmnd/<topic>/TuyaSend1 6,1
```

## Documentation

- [Home Assistant setup](docs/HomeAssistant.md)
- [Tasmota setup](docs/Tasmota.md)
- [Datapoint and MQTT mapping](docs/Mapping.md)
- [TYWE3S flashing notes](docs/Flash_TYWE3S.md)
- [Example MQTT topics](examples/mqtt_topics.md)

## Safety

Wall thermostats are mains-powered devices. Disconnect power before opening the
thermostat, and only flash or wire the device if you are qualified to work with
mains electricity. Incorrect wiring can damage heating equipment or create a
dangerous installation.
