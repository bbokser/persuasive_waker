import utils

# import gc  # garbage collector
# print('free memory left before (most) imports: ', gc.mem_free())
# from ulab import numpy as np
import board
import displayio
import terminalio
import vectorio
import busio
import adafruit_ssd1680
import supervisor
from adafruit_display_text.bitmap_label import Label

# print('free memory left after imports: ', gc.mem_free())

supervisor.runtime.autoreload = False

displayio.release_displays()


class InkDisp:
    def __init__(self, cs, dc, reset):
        spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=None)
        # epd_busy = board.GP16
        display_bus = displayio.FourWire(
            spi, command=dc, chip_select=cs, reset=reset, baudrate=1000000
        )
        # time.sleep(1)
        # For issues with display not updating top/bottom rows correctly set colstart to 8
        display = adafruit_ssd1680.SSD1680(
            # for 2.13" 250x122 display (waveshare 12672)
            display_bus,
            colstart=0,
            width=250,
            height=122,
            highlight_color=0xFF0000,
            rotation=270,
        )
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

    def clear(self):
        # clear the group
        self.g = displayio.Group()

    def update(self):
        # Add the Group to the Display
        self.display.root_group = self.g
        self.display.refresh()

    def get_idx(self, color: str):
        """
        Convert color name to index
        """
        return self.color_names.index(color)

    def draw_text(
        self, text: str, x: int, y: int, color: str = "black", scale: int = 1
    ):
        # display = self.display
        lbl = Label(terminalio.FONT, text=text, color=utils.colors[color], scale=scale)
        lbl.anchor_point = (0.0, 1.0)
        lbl.anchored_position = (x, y)  # (display.width // 2, display.height // 2)
        self.g.append(lbl)
        return None

    def apply_info(self, info: dict):
        display = self.display
        self.draw_bg(color="white")
        x_center = display.width // 2
        col_1 = 5
        col_2 = x_center + 40
        row_1 = 20
        row_2 = row_1 + 20
        row_3 = row_2 + 20
        row_4 = row_3 + 20
        row_5 = row_4 + 20
        row_6 = row_5 + 20

        self.draw_text(text=info["weekday"], x=col_1, y=row_3, scale=5)
        self.draw_text(
            text=info["month"] + " " + info["day"], x=col_1, y=row_4 + 10, scale=3
        )

        self.draw_text(text="Alarm: " + info["alarm"], x=col_1, y=row_6, scale=2)

        if info["usb"]:
            usb_msg = "USB In"
            msg_scale = 2
        else:
            usb_msg = "Batt:" + info["batt"] + "%"
            msg_scale = 1

        self.draw_text(text=usb_msg, x=col_2, y=row_2, scale=msg_scale)

        self.draw_text(text=info["temp"] + " C", x=col_2, y=row_4, scale=2)

        self.draw_text(text=info["humidity"] + " %", x=col_2, y=row_6, scale=2)
        return None

    def draw_polygon(self, points: list, color: str):
        """
        origin = the user's location as a tuple, e.g. (lat, long)
        p = palette
        points = list of tuples e.g. [(1, 2), (2, 2), (3, 4), (5, 6)]
        """
        display = self.display
        polygon = vectorio.Polygon(
            pixel_shader=self.p,
            points=points,
            x=display.width // 2,
            y=display.height // 2,
            color_index=self.get_idx(color),
        )
        self.g.append(polygon)
        return None

    def draw_bg(self, color: str):
        """
        draw background
        """
        display = self.display
        rect = vectorio.Rectangle(
            pixel_shader=self.p,
            width=display.width + 1,
            height=display.height + 1,
            x=0,
            y=0,
            color_index=self.get_idx(color),
        )
        self.g.append(rect)
        return None
