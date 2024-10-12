import board
import digitalio
import analogio

from utils import percentize

class Batt():
    def __init__(self):
        self._v_batt_max = 3
        self._v_batt_min = 1
        self._v_batt = analogio.AnalogIn(board.VOLTAGE_MONITOR)
        self.usb_power = digitalio.DigitalInOut(board.VBUS_SENSE)
    
    def get_batt_frac(self)->float:
        return percentize(self._v_batt.value, min=self._v_batt_min, max=self._v_batt_max)