# PixelWeatherOS Lite
This is an alternative implementation of [PixelWeatherOS](https://github.com/PixelWeatherProject/pwos/) in MicroPython **for comparison purposes** only. It will not be actively developed.

For details see the original version in Rust linked above.

## Installation
You can install this using [`rshell`](https://github.com/dhylands/rshell).

Assuming you're in the root of this repo, you can use *rshell*'s `rsync -m . /pyboard` command to transfer all the scripts to flash.

## Features compared to the Rust version
- [ ] CPU clock defaults to maximum 240MHz
  - Not possible without a custom MP build.
  - The CPU is overclocked at **runtime** instead.
- [ ] Detection and reporting of erros from previous runs
- [ ] Customized optimized logger
- [ ] USB serial detection
  - Not possible without a custom MP build.
- [ ] Browout detector control
- [ ] ESP-IDF version detection
  - Not possible without a custom MP build.
- [x] On-board LED control
- [x] Battery voltage measurement
- [x] Low battery voltage detection (sBOP)
- [x] I2C hardware support
- [x] Runtime application configuration
- [x] Deep sleep
- [ ] Fake sleep (for debugging sessions)
  - Not possible without USB serial detection.
- [x] WiFi support
- [x] Communication with PWMP
  - [x] Can read runtime application configuration
  - [x] Can perform handshake
  - [x] Can send mesurement results
  - [x] Can send stats
  - [ ] Can check for OTA updates
    - Not possible without heavy modifications to the PWMP server.
  - [x] Can send notifications
  - [ ] Type-safe
    - Not possible.
- [x] Interface for multuple environment sensors
- [x] Detection and reporting of abnormal reset reasons
- [ ] OTA support
  - [ ] Auto-rollback if the firmware is not working
    - Possible, but may use a lot of flash storage.
- [ ] Advanced error handling
  - Not possible due to Python.

## Size comparison
|                 | **Firmware (debug)** | **Firmware (release `-O3`)** | **Interpreter** |
| --------------- | -------------------- | ---------------------------- | --------------- |
| **MicroPython** | N/A                  | 180kB<sup>*</sup>            | 1.6MB           |
| **Rust**        | 1.106MB              | 758kB                        | N/A             |

- `*`: Optimization does not exist in this context