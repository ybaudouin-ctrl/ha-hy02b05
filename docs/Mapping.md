# Datapoint And MQTT Mapping

The thermostat is a TuyaMCU device. Tasmota acts as the bridge between MQTT and
the thermostat MCU. HA-HY02B05 maps the MQTT messages into one Home Assistant
climate entity.

## MQTT Topics

Replace `<topic>` with the Tasmota topic entered in the Home Assistant config
flow.

| Topic | Direction | Used for |
| --- | --- | --- |
| `tele/<topic>/SENSOR` | Tasmota -> Home Assistant | Current and target temperature |
| `tele/<topic>/RESULT` | Tasmota -> Home Assistant | Tuya datapoint updates |
| `stat/<topic>/POWER` | Tasmota -> Home Assistant | Relay/power state |
| `cmnd/<topic>/POWER` | Home Assistant -> Tasmota | Turn thermostat on or off |
| `cmnd/<topic>/TuyaSend2` | Home Assistant -> Tasmota | Set target temperature |
| `cmnd/<topic>/TuyaSend4` | Home Assistant -> Tasmota | Set enum datapoints such as mode |

## Datapoints

| DP | Tasmota field or command | Home Assistant mapping |
| --- | --- | --- |
| 1 | `POWER` / relay | HVAC mode `heat` or `off` |
| 2 | `TuyaSend2 2,<value>` | Target temperature |
| 3 | `TuyaSNS.Temperature` | Current temperature |
| 4 | `DpType4Id4` and `TuyaSend4 4,<value>` | Preset mode |
| 6 | `DpType1Id6` | `child_lock_enabled` attribute |

## Temperature Scaling

The thermostat target temperature is sent to Tuya as tenths of a degree Celsius.

| Home Assistant target | MQTT command payload |
| --- | --- |
| 5.0 | `2,50` |
| 19.5 | `2,195` |
| 21.0 | `2,210` |
| 35.0 | `2,350` |

## Preset Values

| Tuya value | Home Assistant preset |
| --- | --- |
| 0 | `manual` |
| 1 | `auto` |
| 2 | `away` |
| 3 | `override` |

## Payload Examples

### Sensor Payload

```json
{
  "TuyaSNS": {
    "Temperature": 20.5,
    "TempSet": 21
  }
}
```

### Mode Payload

```json
{
  "TuyaReceived": {
    "DpType4Id4": 1
  }
}
```

### Child Lock Payload

```json
{
  "TuyaReceived": {
    "DpType1Id6": 1
  }
}
```

## Current Integration Surface

Only the climate platform is loaded by `custom_components/hy02b05/__init__.py`.
That means the current release exposes child lock as a climate attribute rather
than a separate switch entity.
