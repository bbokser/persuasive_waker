import adafruit_sht4x
from busio import I2C


class HTSensor:
    def __init__(self, i2c: I2C):
        self.sht = adafruit_sht4x.SHT4x(i2c)

    def set_mode_read(self):
        self.sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION

    def set_mode_heat(self):
        self.sht.mode = adafruit_sht4x.Mode.LOWHEAT_100MS

    def get_temperature(self):
        return self.sht.temperature

    def get_humidity(self):
        return self.sht.relative_humidity
