
from adafruit_ht16k33 import segments
import board

class SegmentDisp():
    def __init__(self):
        i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        self.segment_disp = segments.Seg14x4(i2c)
    
    def clear(self):
        # Clear the display.
        self.segment_disp.fill(0)

    def print(self, value:str):
        self.segment_disp.print(value)

    def print_2vals(self, value1:str, value2:str):
        value = '{:02d}{:02d}'.format(value1, value2)
        self.segment_disp.print(value)
    