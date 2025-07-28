from busio import I2C

import adafruit_mcp4725


class DAC:
    def __init__(self, i2c: I2C):
        # Initialize MCP4725
        self.mcp4725 = adafruit_mcp4725.MCP4725(i2c)

    def set_value(self, value: float):
        self.mcp4725.normalized_value = value
