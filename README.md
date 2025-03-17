# persuasive_waker
Persuasive Waker is an open source hardware alarm clock that can't be snoozed or turned off. The alarm is deactivated via a remote key fob, which should be placed as far from the user's bed as possible. E.g. in the bathroom.

## Build
The KiCad design files are located in the `hw` folder.

Pending mechanical CAD and additional build instructions.

## Setup
1. Install CircuitPython on your Pico by following [this](https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython) guide.

2. Install [circup](https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/prepare) on your computer.

3. Run the following commands to install all necessary libraries.

    ```
    circup bundle-add adafruit/circuitpython-fonts
    circup install adafruit_sht4x adafruit_ssd1680 adafruit_display_text adafruit_ds3231 adafruit_datetime font_ostrich_sans_black_30 font_ostrich_sans_black_72
    ```
4. Delete `code.py` from the Pico's storage.

5. Clone this repo onto your computer and copy+paste everything in the `src` folder to the Pico's storage.

6. The alarm clock should be functioning now.

## User Manual
See [here](user_manual.md).

# TODO

## Mechanical
- 

## Electrical
### Testing
- 

### Schematic
- Use H-bridge to increase volume

### Footprints
- 

### Board Layout
- Cover: Move icons down a little
- Cover: Prevent order number from being marked

## Software
- Setting to prevent changing alarm last-minute?
- Weekend vs Weekday Alarm
- Option Button
    - Alarm pitch setting
    - Alarm ring time setting
    - Set F vs C
    - Set military vs 12 hour time
    
## Documentation
- Write user manual
- Add mechanical CAD
- Full BoM
- Finish build instructions