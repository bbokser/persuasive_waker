import utils

# import gc  # garbage collector
# print('free memory left before (most) imports: ', gc.mem_free())
# from ulab import numpy as np
import board
import displayio
from fourwire import FourWire
import terminalio
import vectorio
import busio
import adafruit_ssd1680
# import adafruit_spd1656
import supervisor
from adafruit_display_text.bitmap_label import Label

# print('free memory left after imports: ', gc.mem_free())

supervisor.runtime.autoreload = False

displayio.release_displays()


class InkDisp():
    def __init__(self, date_init, alarm_init, batt, usb):
        spi = busio.SPI(board.GP2, MOSI=board.GP19, MISO=None)
        epd_cs = board.GP7
        epd_dc = board.GP3
        epd_reset = board.GP20
        epd_busy = board.GP21
        display_bus = FourWire(
            spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000)

        # For issues with display not updating top/bottom rows correctly set colstart to 8
        display = adafruit_ssd1680.SSD1680(
            # for 2.13" 250x122 display (waveshare 12672)
            display_bus,
            width=250,
            height=122,
            busy_pin=epd_busy,
            highlight_color=0xFF0000,
            rotation=270,
        )

        # display = adafruit_spd1656.SPD1656(
        #     display_bus, width=600, height=448, busy_pin=epd_busy)

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

        # initialization routine
        self.draw_bg(color='white')
        self.apply_info(date=date_init, alarm=alarm_init, batt=batt, usb=usb)
        self.update()
    
    def clear(self):
        # clear the group
        self.g = displayio.Group()

    def update(self):
        # Add the Group to the Display
        self.display.root_group = self.g
        self.display.refresh()

    def get_idx(self, color: str):
        '''
        Convert color name to index
        '''
        return self.color_names.index(color)
    
    def draw_text(self, text: str, x: int, y: int, color: str):
        # display = self.display
        lbl = Label(terminalio.FONT, text=text, color=utils.colors[color], scale=3)
        lbl.anchor_point = (0.5, 0.5)
        lbl.anchored_position = (x, y)  # (display.width // 2, display.height // 2) 
        self.g.append(lbl)
        return None
    
    def apply_info(self, date:str, alarm:str, batt:float, usb:float):
        display = self.display
        self.draw_text(text=date, 
                       x=display.width // 2, y=display.height // 2 + 15, color='black')
        self.draw_text(text='Alarm: ' + alarm, 
                       x=display.width // 2, y=display.height // 2, color='black')
        self.draw_text(text='Batt: ' + str(batt * 100) + '%', 
                       x=display.width // 2, y=display.height // 2 - 15, color='black')
        usb_msg = 'USB In' if usb else 'Unplugged'
        self.draw_text(text=usb_msg, 
                       x=display.width // 2, y=display.height // 2 - 30, color='black')
        return None
    
    def draw_polygon(self, points: list, color: str):
        '''
        origin = the user's location as a tuple, e.g. (lat, long)
        p = palette
        points = list of tuples e.g. [(1, 2), (2, 2), (3, 4), (5, 6)]
        '''
        display = self.display
        polygon = vectorio.Polygon(pixel_shader=self.p, 
                                   points=points, 
                                   x=display.width // 2,
                                   y=display.height // 2, 
                                   color_index=self.get_idx(color))
        self.g.append(polygon)
        return None
    
    def draw_bg(self, color: str):
        '''
        draw background
        '''
        display = self.display
        rect = vectorio.Rectangle(pixel_shader=self.p, 
                                  width=display.width, 
                                  height=display.height, 
                                  x=0, 
                                  y=0, 
                                  color_index=self.get_idx(color))
        self.g.append(rect)
        return None
