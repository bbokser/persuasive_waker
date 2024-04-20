
from adafruit_ht16k33 import segments
import board

class SegmentDisp():
    def __init__(self):
        i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        self.segment_disp = segments.Seg14x4(i2c)
    
    def clear(self):
        # Clear the display.
        self.segment_disp.fill(0)

    def print(self, value:int, blink:bool=False):
        if blink:
            self.segment_disp.print('    ')
        else:
            self.segment_disp.print(value)

    def print_2vals(self, value1:int, value2:int, wink_left:bool=False, wink_right:bool=False):
        if wink_left:
            value = '  {:02d}'.format(value2)
        elif wink_right:
            value = '{:02d}  '.format(value1)
        else:
            value = '{:02d}{:02d}'.format(value1, value2)
        self.segment_disp.print(value)
    