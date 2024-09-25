
from as1115 import AS1115
import board

def nthdigit(value:int, idx:int):
    return value // 10**idx % 10

class SegmentDisp():
    def __init__(self):
        i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        self.segment_disp = AS1115(i2c)
    
    def clear(self):
        # Clear the display.
        self.segment_disp.clear()

    def print(self, value:int, blink:bool=False):
        if blink:
            self.segment_disp.clear()
        else:
            self.segment_disp.display_int(value)

    def print_2vals(self, value1:int, value2:int, wink_left:bool=False, wink_right:bool=False):
        if wink_left:
            self.segment_disp.clear_idx(0)
            self.segment_disp.clear_idx(1)
            self.segment_disp.display_idx(2, nthdigit(value2, 0))
            self.segment_disp.display_idx(3, nthdigit(value2, 1))
        elif wink_right:
            self.segment_disp.display_idx(0, nthdigit(value1, 0))
            self.segment_disp.display_idx(1, nthdigit(value1, 1))
            self.segment_disp.clear_idx(2)
            self.segment_disp.clear_idx(3)
        else:
            self.segment_disp.display_int(int(str(value1) + str(value2)))
    