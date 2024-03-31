import time

import utils
from inkdisp import InkDisp
from clock import Clock
from segment import SegmentDisp

time.sleep(5)  # to ensure serial connection does not fail

inkdisp = InkDisp()
segment_disp = SegmentDisp()
clock = Clock()
date_str = clock.get_date_str()

inkdisp.add_bg(c_border=utils.colors['green'], c_fill=utils.colors['white'], border_len=5)
# disp.display_text(time_display, x=disp.width//2, y=disp.height//2)
inkdisp.add_text(date_str, x=inkdisp.width//2, y=inkdisp.height//2 - 50)
inkdisp.update()

while True:
    hour, min = clock.get_time()
    segment_disp.show_time(hour, min)
    time.sleep(1)
