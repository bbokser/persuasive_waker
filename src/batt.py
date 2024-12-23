import digitalio
import analogio

from utils import percentize


class Batt:
    def __init__(self, pin_vbatt, pin_usb):
        self._v_batt_max = 3
        self._v_batt_min = 1
        self._v_batt = analogio.AnalogIn(pin_vbatt)
        self.usb_power = digitalio.DigitalInOut(pin_usb)

    def get_batt_frac(self) -> float:
        volts = self._v_batt.value * 3.3 / 65536
        return percentize(volts, min=self._v_batt_min, max=self._v_batt_max)

    def get_batt_str(self) -> str:
        return "{:.1f}".format(self.get_batt_frac() * 100)
