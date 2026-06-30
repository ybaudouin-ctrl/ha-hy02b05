# TYWE3S Flashing Notes

Many HY02B05/Floureon thermostats use a Tuya TYWE3S ESP8266 Wi-Fi module. This
page is a project note, not a full flashing guide.

## Safety First

Wall thermostats are mains-powered. Disconnect power before opening the device.
Do not connect a USB serial adapter while the thermostat is connected to mains
power. Work only if you understand mains isolation and low-voltage serial
flashing.

## Goal

The goal is to replace the stock Tuya firmware on the Wi-Fi module with Tasmota.
After that, Tasmota communicates with the thermostat MCU over serial and exposes
the MCU datapoints over MQTT.

## Typical Process

1. Open the thermostat and identify the TYWE3S module.
2. Locate `3V3`, `GND`, `TX`, `RX`, and `GPIO0`.
3. Use a 3.3 V serial adapter.
4. Pull `GPIO0` to `GND` during boot to enter flashing mode.
5. Flash a Tasmota build that supports TuyaMCU.
6. Configure Wi-Fi and MQTT in Tasmota.
7. Configure the module as TuyaMCU if needed.
8. Verify that Tasmota publishes `TuyaSNS` and `TuyaReceived` data.

## After Flashing

Configure Tasmota MQTT and Tuya reporting as described in
[Tasmota setup](Tasmota.md). Home Assistant should not be configured until
Tasmota is publishing stable MQTT messages.

## Recovery Notes

If the device does not boot after flashing:

- Confirm the serial adapter is 3.3 V, not 5 V.
- Check TX/RX are crossed.
- Check whether GPIO0 is still held low.
- Check that the thermostat is not connected to mains while serial wiring is
  attached.
- Reflash Tasmota with erase before write if the device is in an unknown state.
