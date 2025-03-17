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
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.bitmap_label import Label
from font_ostrich_sans_black_30 import FONT as font_30
from font_ostrich_sans_black_72 import FONT as font_72

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

    def draw_bmp(self, path: str, x: int, y: int):
        odb = displayio.OnDiskBitmap(path)
        image = displayio.TileGrid(odb, pixel_shader=odb.pixel_shader, x=x, y=y)
        self.g.append(image)

    def draw_text(self, text: str, x: int, y: int, color: str = "black", opt: int = 1):
        # display = self.display
        # lbl = Label(terminalio.FONT, text=text, color=utils.colors[color], scale=scale)
        if opt == 1:
            font = font_30
        elif opt == 2:
            font = font_72
        else:
            raise Exception("Invalid font")
        lbl = Label(font, text=text, color=utils.colors[color], scale=1)
        lbl.anchor_point = (0.0, 1.0)
        lbl.anchored_position = (x, y)  # (display.width // 2, display.height // 2)
        self.g.append(lbl)
        return None

    def apply_info(self, info: dict):
        display = self.display
        self.draw_bg(color="white")
        x_center = display.width // 2
        col_1 = 5
        col_2 = x_center
        row_1 = 24
        row_2 = row_1 + 30
        row_3 = row_2 + 30
        row_4 = row_3 + 30
        offset_icon = 18
        offset_txt = 24

        self.draw_text(text=info["weekday"], x=col_1, y=50, opt=2)
        self.draw_text(text=info["month"] + " " + info["day"], x=col_1, y=row_3)
        self.draw_bmp("/bmps/alarm1.bmp", x=col_1, y=row_4 - offset_icon)
        self.draw_text(text=info["alarm1"], x=col_1 + offset_txt, y=row_4)

        self.draw_bmp("/bmps/elec.bmp", x=col_2, y=row_1 - offset_icon)
        if info["usb"]:
            self.draw_text(text="USB", x=col_2 + offset_txt, y=row_1)
        else:
            self.draw_battery(frac=info["batt"], x=col_2 + offset_txt, y=5)

        self.draw_bmp("/bmps/temp.bmp", x=col_2, y=row_2 - offset_icon)
        self.draw_text(text=info["temp"] + " C", x=col_2 + offset_txt, y=row_2)

        self.draw_bmp("/bmps/humidity.bmp", x=col_2, y=row_3 - offset_icon)
        self.draw_text(text=info["humidity"] + " %", x=col_2 + offset_txt, y=row_3)

        self.draw_bmp("/bmps/alarm2.bmp", x=col_2, y=row_4 - offset_icon)
        self.draw_text(text=info["alarm2"], x=col_2 + offset_txt, y=row_4)
        return None

    def draw_battery(self, frac, x, y):
        frac = utils.clip(frac, 0, 1)
        clearance = 2
        height = 20
        width_max = 40
        case = Rect(x, y, width_max, height, fill=None, outline=utils.colors["black"])
        fill = Rect(
            x + clearance,
            y + clearance,
            int(frac * width_max) - clearance * 2,
            height - clearance * 2,
            fill=utils.colors["black"],
        )
        nub = Rect(
            x + width_max,
            y + int(height / 4),
            5,
            int(height / 2),
            fill=utils.colors["black"],
        )
        self.g.append(case)
        self.g.append(fill)
        self.g.append(nub)

    def draw_polygon(self, points: list, color: str):
        """
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
