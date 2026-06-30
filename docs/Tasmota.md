# Tasmota Setup

HA-HY02B05 expects a HY02B05/Floureon thermostat running Tasmota in TuyaMCU mode.
The integration reads Tasmota MQTT output and sends Tasmota MQTT commands; it
does not talk to the Tuya MCU directly.

## MQTT

Configure Tasmota MQTT with:

- MQTT enabled.
- Host, port, user, and password for your broker.
- A unique `Topic`.
- Default `FullTopic`:

```text
%prefix%/%topic%/
```

Example topic:

```text
Therm_UG_Bureau
```

With the default full topic, Tasmota publishes and receives:

```text
tele/Therm_UG_Bureau/SENSOR
tele/Therm_UG_Bureau/RESULT
stat/Therm_UG_Bureau/POWER
cmnd/Therm_UG_Bureau/POWER
cmnd/Therm_UG_Bureau/TuyaSend2
cmnd/Therm_UG_Bureau/TuyaSend4
```

## Recommended Console Commands

Run these from the Tasmota web console:

```text
SetOption66 1
TelePeriod 300
```

Meaning:

- `SetOption66 1` publishes decoded `TuyaReceived` payloads to MQTT.
- `TelePeriod 300` publishes telemetry every 300 seconds.

## Verify Telemetry

Subscribe to:

```text
tele/<topic>/SENSOR
```

Expected shape:

```json
{
  "Time": "2026-06-30T12:00:00",
  "TuyaSNS": {
    "Temperature": 20.5,
    "TempSet": 21
  }
}
```

The integration reads:

- `TuyaSNS.Temperature` as current room temperature.
- `TuyaSNS.TempSet` as target temperature.

## Verify Power

Subscribe to:

```text
stat/<topic>/POWER
```

Expected payload:

```text
ON
```

or:

```text
OFF
```

The integration maps `ON` to Home Assistant `heat` and `OFF` to Home Assistant
`off`.

## Verify Tuya Datapoints

Subscribe to:

```text
tele/<topic>/RESULT
```

Expected mode or child lock payload:

```json
{
  "TuyaReceived": {
    "DpType4Id4": 0,
    "DpType1Id6": 0
  }
}
```

The integration reads:

- `DpType4Id4` as preset mode.
- `DpType1Id6` as child lock state.

## Commands Sent By The Integration

Power:

```text
Topic:   cmnd/<topic>/POWER
Payload: ON
```

Target temperature:

```text
Topic:   cmnd/<topic>/TuyaSend2
Payload: 2,210
```

`210` means 21.0 degrees Celsius.

Preset mode:

```text
Topic:   cmnd/<topic>/TuyaSend4
Payload: 4,0
```

Mode values:

| Value | Home Assistant preset |
| --- | --- |
| 0 | `manual` |
| 1 | `auto` |
| 2 | `away` |
| 3 | `override` |
