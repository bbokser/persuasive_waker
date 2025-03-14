# persuasive_waker
Persuasive Waker is an open source hardware alarm clock that can't be snoozed or turned off. The alarm is deactivated via a remote key fob, which should be placed as far from the user's bed as possible. E.g. in the bathroom.

## Build
The KiCad design files are located in the `hw` folder.

Pending mechanical CAD and additional build instructions.

## Setup
1. Install CircuitPython on your Pico by following [this](https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython) guide.

2. Install [circup](https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/prepare) on your computer.

3. Run the following command to install all necessary libraries.

    ```
    circup install adafruit_sht4x adafruit_ssd1680 adafruit_display_text adafruit_ds3231 adafruit_datetime
    ```
4. Delete `code.py` from the Pico's storage.

5. Clone this repo onto your computer and copy+paste everything in the `src` folder to the Pico's storage.

6. The alarm clock should be functioning now.

## User Manual
See [here](user_manual.md).

# TODO

## Mechanical
- All done

## Electrical
### Testing
- All done

### Schematic
- All done

### Footprints
- All done

### Board Layout
- Cover: Move icons down a little
- Cover: Prevent order number from being marked

## Software
- Second Alarm
- Weekend vs Weekday Alarm
- Option Button
    - Way to set F vs C
    - Way to set military vs 12 hour time
- Improve batt percentage
    
## Documentation
- Write user manual
- Add mechanical CAD
- Full BoM
- Finish build instructions