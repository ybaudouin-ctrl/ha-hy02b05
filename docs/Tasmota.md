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
stat/Therm_UG_Bureau/POWER1
stat/Therm_UG_Bureau/POWER2
cmnd/Therm_UG_Bureau/POWER
cmnd/Therm_UG_Bureau/TuyaSend2
cmnd/Therm_UG_Bureau/TuyaSend1
cmnd/Therm_UG_Bureau/TuyaSend4
```

## Recommended Console Commands

Run this from the Tasmota web console:

```text
Backlog Module 54; TuyaMCU 11,1; TuyaMCU 72,2; TuyaMCU 71,3; TuyaMCU 26,4; TuyaMCU 12,102; SetOption66 1; TempRes 1; TelePeriod 30; Timezone 99; NtpServer1 pool.ntp.org; NtpServer2 time.google.com; NtpServer3 time.cloudflare.com; Restart 1
```

Meaning:

- `Module 54` sets the module type to TYWE3S (Wi-Fi thermostat).
- `TuyaMCU 11,1` maps Tuya datapoint 1 (power/relay) to Tasmota relay 1.
- `TuyaMCU 72,2` maps Tuya datapoint 2 (target temperature) to Tasmota virtual switch 2.
- `TuyaMCU 71,3` maps Tuya datapoint 3 (current temperature) to Tasmota virtual sensor 3.
- `TuyaMCU 26,4` maps Tuya datapoint 4 (operating mode) to Tasmota function 26 slot 4.
- `TuyaMCU 12,102` maps Tuya datapoint 102 (physical heating relay state) to Tasmota relay 2 (`POWER2`).
- `SetOption66 1` publishes decoded `TuyaReceived` payloads to MQTT.
- `TempRes 1` sets temperature resolution to 1 decimal place.
- `TelePeriod 30` publishes telemetry every 30 seconds (fast updates).
- `Timezone 99` sets timezone to UTC.
- `NtpServer1 pool.ntp.org`, `NtpServer2 time.google.com`, `NtpServer3 time.cloudflare.com` configure NTP time synchronization.
- `Restart 1` applies all changes and restarts the device.

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

`POWER` or `POWER1` (Tuya DP1) controls thermostat power and drives the climate
entity's `heat`/`off` state. `POWER2` (Tuya DP102) reports
the physical heating relay and drives the separate Home Assistant heating
binary sensor (`heat` device class, fire icon). The sensor remains unknown until
the first valid `POWER2` message arrives.

For multi-relay devices, Tasmota can publish both relay states in
`tele/<topic>/STATE` as `POWER1` and `POWER2`; the integration reads those fields
as well as the individual status topics.

Subscribe to:

```text
stat/<topic>/POWER2
```

Expected payloads are `ON` while heating is active and `OFF` otherwise. Confirm
this mapping on each thermostat before relying on the sensor.

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

Child lock:

```text
Topic:   cmnd/<topic>/TuyaSend1
Payload: 6,1
```

Child lock values:

| Value | Meaning |
| --- | --- |
| 0 | unlocked |
| 1 | locked |
