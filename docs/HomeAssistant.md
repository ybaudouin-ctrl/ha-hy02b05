# Home Assistant Setup

This integration is configured from the Home Assistant UI. It does not use
`configuration.yaml`.

## Install

### HACS

1. Open HACS in Home Assistant.
2. Add this GitHub repository as a custom repository.
3. Select category `Integration`.
4. Download `HY02B05 Thermostat`.
5. Restart Home Assistant.

### Manual

Copy the integration folder into Home Assistant:

```text
config/custom_components/hy02b05/
```

Restart Home Assistant after copying the files.

## Add The Thermostat

1. Go to Settings -> Devices & services.
2. Select Add integration.
3. Search for `HY02B05 Thermostat`.
4. Enter a name.
5. Enter the Tasmota MQTT topic.

The topic is the Tasmota `%topic%` value. If Tasmota publishes:

```text
tele/Therm_UG_Bureau/SENSOR
```

enter:

```text
Therm_UG_Bureau
```

## MQTT Requirement

Home Assistant must already have the MQTT integration configured and connected to
the same broker as Tasmota. This custom integration uses Home Assistant's MQTT
integration to subscribe and publish; it does not create its own broker
connection.

## Entity

The current release creates one climate entity.

| Feature | Value |
| --- | --- |
| Platform | `climate` |
| HVAC modes | `off`, `heat` |
| Temperature unit | Celsius |
| Target range | 5 to 35 |
| Target step | 0.5 |
| Presets | `manual`, `auto`, `away`, `override` |
| Extra attribute | `child_lock_enabled` |

## Availability

The entity starts unavailable. It becomes available after the integration receives
one valid message from any of these topics:

```text
tele/<topic>/SENSOR
tele/<topic>/RESULT
stat/<topic>/POWER
```

If the entity stays unavailable, verify that the Tasmota topic entered in the
config flow exactly matches the topic in MQTT.

## Removing

Remove the config entry from Settings -> Devices & services. Home Assistant will
unload the MQTT subscriptions for that thermostat.
