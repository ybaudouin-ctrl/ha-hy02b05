# MQTT Topic Examples

Example Tasmota topic:

```text
Therm_UG_Bureau
```

## Subscribe

Use these subscriptions to see what Home Assistant will receive:

```text
tele/Therm_UG_Bureau/SENSOR
tele/Therm_UG_Bureau/RESULT
stat/Therm_UG_Bureau/POWER
```

## Publish Commands

Turn thermostat on:

```text
Topic:   cmnd/Therm_UG_Bureau/POWER
Payload: ON
```

Turn thermostat off:

```text
Topic:   cmnd/Therm_UG_Bureau/POWER
Payload: OFF
```

Set target temperature to 21.0 degrees Celsius:

```text
Topic:   cmnd/Therm_UG_Bureau/TuyaSend2
Payload: 2,210
```

Set manual mode:

```text
Topic:   cmnd/Therm_UG_Bureau/TuyaSend4
Payload: 4,0
```

Set auto mode:

```text
Topic:   cmnd/Therm_UG_Bureau/TuyaSend4
Payload: 4,1
```

Set away mode:

```text
Topic:   cmnd/Therm_UG_Bureau/TuyaSend4
Payload: 4,2
```

Set override mode:

```text
Topic:   cmnd/Therm_UG_Bureau/TuyaSend4
Payload: 4,3
```

## Expected Payloads

Sensor:

```json
{
  "Time": "2026-06-30T12:00:00",
  "TuyaSNS": {
    "Temperature": 20.5,
    "TempSet": 21
  }
}
```

Power:

```text
ON
```

Tuya result:

```json
{
  "TuyaReceived": {
    "DpType4Id4": 0,
    "DpType1Id6": 0
  }
}
```
