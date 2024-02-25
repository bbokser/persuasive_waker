import time
import rtc

import utils
from disp import DispRunner

class RTC(object):
    @property
    def datetime(self):
        return time.struct_time((2024, 2, 25, 21, 1, 47, 6, 0, 0))
                              # [year,month,day,hour,minute,second, weekday, yearday, isdst]

def get_suffix(n: int):
    last_digit = n % 10
    return utils.number_suffix[last_digit]

time.sleep(5)  # to ensure serial connection does not fail
r = RTC()
rtc.set_time_source(r)    

current = r.datetime

hour = current.tm_hour % 12
if hour == 0:
    hour = 12

am_pm = "AM"
if current.tm_hour / 12 >= 1:
    am_pm = "PM"

weekday = utils.weekday[current.tm_wday]
month = utils.month[current.tm_mon - 1]
suffix = get_suffix(current.tm_mday)

time_display = "{:d}:{:02d}:{:02d} {}".format(hour, current.tm_min, current.tm_sec, am_pm)
# date_display = "{:d}/{:d}/{:d}".format(current.tm_mon, current.tm_mday, current.tm_year)
date_display = "{}, {} {:d}{}, {:d}".format(weekday, month, current.tm_mday, suffix, current.tm_year)

disp = DispRunner()
disp.display_bg(c_border=utils.colors['green'], c_fill=utils.colors['white'], border_len=5)
disp.display_text(time_display, x=disp.width//2, y=disp.height//2)
disp.display_text(date_display, x=disp.width//2, y=disp.height//2 - 50)
disp.run()

while True:
    # current_time = r.datetime
    # print(current_time)
    
    pass
