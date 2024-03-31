'''For 5.6' 600x448 7-color ACeP display
'''

import utils

# import gc  # garbage collector
# print('free memory left before (most) imports: ', gc.mem_free())
# from ulab import numpy as np
import board
import displayio
import terminalio
import vectorio
import busio
import adafruit_spd1656
import supervisor
from adafruit_display_text.bitmap_label import Label

# print('free memory left after imports: ', gc.mem_free())

supervisor.runtime.autoreload = False

displayio.release_displays()


class InkDisp():
    def __init__(self):       
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
        
    def update(self):
        # Add the Group to the Display
        self.display.root_group = self.g
        self.display.refresh()

    def get_idx(self, color: str):
        '''
        Convert color name to index
        '''
        return self.color_names.index(color)
    
    def add_text(self, text: str, x: int, y: int, color: str):
        # display = self.display
        lbl = Label(terminalio.FONT, text=text, color=utils.colors[color], scale=3)
        lbl.anchor_point = (0.5, 0.5)
        lbl.anchored_position = (x, y)  # (display.width // 2, display.height // 2)
        self.g.append(lbl)
        return None
    
    def draw_polygon(self, points: list, color: str):
        '''
        origin = the user's location as a tuple, e.g. (lat, long)
        p = palette
        points = list of tuples e.g. [(1, 2), (2, 2), (3, 4), (5, 6)]
        '''
        display = self.display
        for i in range(len(points)):
            lat, lon = points[i]
            points[i] = self.coord_to_display(self.lat0, self.lon0, lat, lon)
        
        polygon = vectorio.Polygon(pixel_shader=self.p, points=points, x=display.width // 2, y=display.height // 2, color_index=self.get_idx(color))
        self.g.append(polygon)
        return None
    
    def draw_bg(self, color: str):
        '''
        draw background
        '''
        display = self.display
        x = display.width // 2
        y = display.height // 2
        points = [(-x, y), (-x, -y), (x, -y), (x, y)]
        self.draw_polygon(self, points=points, color=color)
        return None
