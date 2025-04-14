# persuasive_waker: User Manual
## Getting Started
1. Install two AA batteries in the battery compartment.
2. Using the provided screws, screw the back plate onto the case with the batteries on the inner side.
3. Connect the clock to a power source via the USB cable. 
4. Holding down the key fob button, press the date button and select the year by rotating the knob. Press the knob inwards to hit "enter".
5. You will now be asked to enter in the month, followed by the day of the month.
6. Press the time button to set the time of day in a similar manner. 

You can only enter the date, time, and alarm setting mode while simultaneously holding down the key fob button. Otherwise, the device will simply emit an "error" sound effect. This feature is meant to prevent your future self from simply changing the alarm setting (or date/time) a minute before the alarm goes off to avoid getting out of bed.

> [!WARNING]  
> Do not rely on the batteries for power. They will run out fairly quickly. The batteries are for backup power--to prevent pulling the plug from stopping the alarm.

> [!WARNING]  
> Do not attempt to use non-alkaline batteries.

## A Note About the Screen
The screen is E-paper. E-paper cannot refresh as quickly as most other display types. The display is set to refresh only once every three minutes. This means you will have to wait a few minutes for changes to the date and alarm to show up on the screen.

## Using the Alarm
- After setting the alarm hour and time, the display will switch to showing seven lines, which represent the days of the week. You can choose between setting the alarm for all seven days, just workdays, or just weekends.
- If you wish to cancel your alarm, press the alarm button and then press the "back" button.
- You can enter the second alarm setting mode by pressing the alarm button twice in a row.
- Press the button on the key fob to deactivate the alarm when it sounds. 

I recommend keeping the key fob far away from your bed, probably in the bathroom. But not so far that it's out of range. You should test it before you put it to use--the range will vary depending on your walls.

## Additional Functionality
- The brightness button will allow you to set the screen brightness.
- Hit the option button once to choose your preferred units for temperature.
- Hit the option button twice to set the alarm's pitch. 
- Try the RESET button if the device seems to be stuck in a bad state. But please notify me if this happens. Or create an [issue](https://github.com/bbokser/persuasive_waker/issues).

> [!NOTE]  
> If you press the RESET button, the E-paper screen will temporarily stop showing the alarm time even though the alarm is still enabled. This is a known issue due to the alarm time being stored in the RTC (clock) chip, not the microprocessor. Transfering this data from the RTC to the microprocessor may require modifications to the [`adafruit_ds3231`](https://docs.circuitpython.org/projects/ds3231/en/latest/api.html#adafruit_ds3231.DS3231.alarm1) library, which I haven't gotten around to. You will have to set the alarm again to make it show.

## Pairing With a New Key Fob
The remote switch receiver is an [RX480E](https://qiachip.com/products/2x-learning-code-receiver-module-for-rf-433mhz-rx-480-e-remote-control-arduino-chip-28131mm-pcb). Use the following instructions to pair a new key fob with your alarm clock (This won't be necessary straight out of the box).

1. Delete existing data by pressing the RF PROG button 8 times. You should see the LED flash 7 times.
2. Learn the new remote by pressing the RF PROG button once. (Note that if you instead press the button twice or thrice in a row, you'll go into other modes, such as toggle mode, which aren't useful for this device. See the link above for more details).
3. The LED should light up, at which point you should press the button on the key fob.
4. You should see the LED flash 3 times. From now on the LED should light up whenever you hit the remote button.

## Updating or Modifying the Software
To update your software (if there are updates), you should follow the instructions in the README.