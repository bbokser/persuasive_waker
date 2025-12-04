from adafruit_onewire.bus import OneWireBus
from adafruit_ds18x20 import DS18X20


class Probe:
    def __init__(self, pin) -> None:
        ow_bus = OneWireBus(pin)
        self.ds18 = DS18X20(ow_bus, ow_bus.scan()[0])

    def get_temp_str(self) -> str:
        try:
            temp = self.ds18.temperature
        except:
            temp = None
        return str(temp)
