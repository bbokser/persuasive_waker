'''For 5.6' 600x448 7-color ACeP display
'''

import utils

# import gc  # garbage collector
# print("free memory left before (most) imports: ", gc.mem_free())
from ulab import numpy as np
import board
import displayio
import terminalio
import bitmaptools
import busio
import adafruit_spd1656
import supervisor
from adafruit_display_text.bitmap_label import Label

# print("free memory left after imports: ", gc.mem_free())

supervisor.runtime.autoreload = False

displayio.release_displays()


class DispRunner:
    def __init__(self):
        '''
        origin: the user's location as a tuple, e.g. (lat, long)
        radius: the radius of a circle that would fit on the screen, in meters
        '''
        
        # this pinout is for the Feather RP2040 ThinkInk
        spi = busio.SPI(board.EPD_SCK, MOSI=board.EPD_MOSI, MISO=None)
        epd_cs = board.EPD_CS
        epd_dc = board.EPD_DC
        epd_reset = board.EPD_RESET
        epd_busy = board.EPD_BUSY
        display_bus = displayio.FourWire(
            spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000)

        # create display object
        display = adafruit_spd1656.SPD1656(
            display_bus, width=600, height=448, busy_pin=epd_busy)

        # create displayio group
        g = displayio.Group()

        # create palette
        color_list = list(utils.colors.values())
        self.color_names = list(utils.colors.keys())
        n = len(color_list)
        p = displayio.Palette(n)
        for i in range(0, n):
            p[i] = color_list[i]

        self.display = display
        self.width = display.width
        self.height = display.height
        self.g = g
        self.p = p
        
        self.color_list = color_list
        
    def run(self):
        display = self.display
        g = self.g
        # Add the Group to the Display
        display.show(g)
        display.refresh()

    def get_idx(self, color: str):
        '''
        Convert color name to index
        '''
        return self.color_names.index(color)
    
    def display_text(self, text: str, x: int, y: int):
        display = self.display
        lbl = Label(terminalio.FONT, text=text, color=utils.colors["black"], scale=3)
        lbl.anchor_point = (0.5, 0.5)
        lbl.anchored_position = (x, y)  # (display.width // 2, display.height // 2)
        self.g.append(lbl)
        return None
    
    def display_bg(self, c_border: int, c_fill: int, border_len: int):
        """
        c_border_len: color of border, hex
        c_fill: color of fill, hex
        border_len: border length (pixels)
        """
        display = self.display
        bmp = displayio.Bitmap(display.width, display.height, 7)
        p = displayio.Palette(2)
        p[0] = c_border
        p[1] = c_fill
        bmp.fill(0)  # Fills the bitmap with the supplied palette index value.
        bitmaptools.fill_region(bmp, 
                                border_len, 
                                border_len, 
                                display.width - border_len, 
                                display.height - border_len, 
                                1)  # create rectangle, fill it w/ p[1]
        tg = displayio.TileGrid(bitmap=bmp, pixel_shader=p)  # Create a TileGrid to hold the bitmap
        self.g.append(tg)
        return None
