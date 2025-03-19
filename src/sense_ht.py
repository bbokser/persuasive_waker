import adafruit_sht4x
from busio import I2C


class HTSensor:
    def __init__(self, i2c: I2C, address: int, units: int):
        self.sht = adafruit_sht4x.SHT4x(i2c, address=address)
        self.change_units(units)

    def change_units(self, units: int):
        self.units = units
        if units == 0:
            self.get_temperature = self.get_temperature_celsius
        else:
            self.get_temperature = self.get_temperature_fahrenheit

    def set_mode_read(self):
        self.sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION

    def set_mode_heat(self):
        self.sht.mode = adafruit_sht4x.Mode.LOWHEAT_100MS

    def get_temperature_celsius(self) -> str:
        return "{:.1f} C".format(round(self.sht.temperature, 1))

    def get_temperature_fahrenheit(self) -> str:
        return "{:.1f} F".format(round(self.sht.temperature * 9 / 5 + 32, 1))

    def get_humidity(self) -> str:
        return "{:.1f}".format(round(self.sht.relative_humidity, 1))
