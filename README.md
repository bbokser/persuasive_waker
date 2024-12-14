# rp2040-alarm-clock

# TODO

## Mechanical
- Top Cover

## Electrical
### Schematic
- Consider whether we really need the interrupts on MAX31328 and AS1115
- Does the encoder really need an EMI filter?

### Footprints
- Done

### Board Layout
- Done

## Software
- Encoder 1 increment per tick, not per 2 ticks
- Add functionality to figure out day of week...?
- Make e-ink update for any of the displayed info changing
- Figure out why variable_frequency is invalid
- Integrate FSM better
- Improve IR accuracy (or switch to better method)
- Piezo music
- Get temperature reading from DS3231
- Gradual vs immediate alarm setting?
- The midnight-crossing problem
- Lowest brightness setting won't have visible winking
- Make disp blink when alarm sounds 
    - temp disabled because blinking interferes with button presses

## Available Pins
board.A0 board.GP26 board.GP26_A0 (GPIO26)
board.A1 board.GP27 board.GP27_A1 (GPIO27)
board.A2 board.GP28 board.GP28_A2 (GPIO28)
board.A3 board.VOLTAGE_MONITOR (GPIO29)
board.GP0 (GPIO0)
board.GP1 (GPIO1)
board.GP10 (GPIO10)
board.GP11 (GPIO11)
board.GP12 (GPIO12)
board.GP13 (GPIO13)
board.GP14 (GPIO14)
board.GP15 (GPIO15)
board.GP16 (GPIO16)
board.GP17 (GPIO17)
board.GP18 (GPIO18)
board.GP19 (GPIO19)
board.GP2 (GPIO2)
board.GP20 (GPIO20)
board.GP21 (GPIO21)
board.GP22 (GPIO22)
board.GP23 board.SMPS_MODE (GPIO23)
board.GP24 board.VBUS_SENSE (GPIO24)
board.GP25 board.LED (GPIO25)
board.GP3 (GPIO3)
board.GP4 (GPIO4)
board.GP5 (GPIO5)
board.GP6 (GPIO6)
board.GP7 (GPIO7)
board.GP8 (GPIO8)
board.GP9 (GPIO9)