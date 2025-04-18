import digitalio
import analogio

from utils import percentize


class Batt:
    def __init__(self, pin_vbatt, pin_usb):
        self._v_batt_max = 3.3
        self._v_batt_min = 1.8  # this is the min volt. for raspi pico
        self._v_batt = analogio.AnalogIn(pin_vbatt)
        self.usb_power = digitalio.DigitalInOut(pin_usb)

    def get_batt_frac(self) -> float:
        # https://forums.raspberrypi.com/viewtopic.php?t=301152
        volts = self._v_batt.value * 3.3 / 65535 * 3
        return percentize(volts, min=self._v_batt_min, max=self._v_batt_max)

    def get_batt_str(self) -> str:
        return "{:.1f}".format(self.get_batt_frac() * 100)
