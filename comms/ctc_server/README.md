# CTC Server

This server was run on a SEEED XIAO ESP32C6

Programmed with Arduino IDE 2.3.10
- In board manager make sure "esp32" by Espressif Systems is Installed
- I did not install additional package libraries for this project
- I used the preinstaled BLE package, by Neil Kolban. This can probably be installed manually ifneedbe. Git is here: https://github.com/nkolban/ESP32_BLE_Arduino
- Board Selection: Board -> esp32 -> XIAO_ESP32C6
- Uses D10 (GPIO19) as output pin

# Actuation

- The ESP32 simply waits for the characteristic flag to go high
- When the characteristic flag is set high, it starts a timer. The timer is based on delay cycle increments
- While the timer is counting, the D10 pin output is high
- The timer can be added to at any time, allowing the timer to be extended, even if the countdown is already taking place
