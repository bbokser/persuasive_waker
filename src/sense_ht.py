import adafruit_sht4x
from busio import I2C


class HTSensor:
    def __init__(self, i2c: I2C, address: int):
        self.sht = adafruit_sht4x.SHT4x(i2c, address=address)

    def set_mode_read(self):
        self.sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION

    def set_mode_heat(self):
        self.sht.mode = adafruit_sht4x.Mode.LOWHEAT_100MS

    def get_temperature(self) -> str:
        return "{:.1f}".format(round(self.sht.temperature, 1))

    def get_humidity(self) -> str:
        return "{:.1f}".format(round(self.sht.relative_humidity, 1))
