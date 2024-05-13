# SPDX-FileCopyrightText: 2017 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Essentials Storage logging boot.py file"""
import board
import digitalio
import storage
import neopixel
import time

switch = digitalio.DigitalInOut(board.A3)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

if switch.value is True:
    # This is when you want write to the board through USB
    pixel.brightness = 0.1
    pixel.fill((0, 0, 255))  # Blue
else:
    # This is for usage
    pixel.brightness = 0.1
    pixel.fill((0, 255, 0))  # Green
time.sleep(2)

# If the switch pin is connected to ground CircuitPython can write to the drive
storage.remount("/", readonly=switch.value)