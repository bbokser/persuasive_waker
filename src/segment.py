
from adafruit_ht16k33 import segments
import board

class SegmentDisp():
    def __init__(self):
        i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        self.segment_disp = segments.Seg14x4(i2c)
    
    def clear(self):
        # Clear the display.
        self.segment_disp.fill(0)

    def show_time(self, hour:int, min:int):
        self.segment_disp.print("{}:{}".format(hour, min))
    