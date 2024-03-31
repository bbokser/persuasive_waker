import adafruit_ds3231
import board
import time
# from ulab import numpy as np

import utils

def get_suffix(n: int):
    last_digit = n % 10
    return utils.number_suffix[last_digit]

class Clock():
    def __init__(self):
        i2c = board.I2C()  #busio.I2C(board.SCL0, board.SDA0)
        self.rtc = adafruit_ds3231.DS3231(i2c)
        self.mday = self.rtc.datetime.tm_mday

    def set_hour(self, value:int):
        self.rtc.datetime = time.struct_time((self.rtc.tm_year, 
                                              self.rtc.tm_mon, 
                                              self.rtc.tm_mday, 
                                              value, 
                                              self.rtc.tm_min, 
                                              self.rtc.tm_sec, 
                                              self.rtc.tm_wday, -1, -1))
        # you must set year, mon, date, hour, min, sec and weekday
        # yearday is not supported, isdst can be set but we don't do anything with it at this time

    def set_min(self, value:int):
        self.rtc.datetime = time.struct_time((self.rtc.tm_year, 
                                              self.rtc.tm_mon, 
                                              self.rtc.tm_mday, 
                                              self.rtc.tm_hour, 
                                              value, 
                                              self.rtc.tm_sec, 
                                              self.rtc.tm_wday, -1, -1))
        # you must set year, mon, date, hour, min, sec and weekday
        # yearday is not supported, isdst can be set but we don't do anything with it at this time

    def get_date_str(self)-> str:
        current = self.rtc.datetime
        weekday = utils.weekday[current.tm_wday]
        month = utils.month[current.tm_mon - 1]
        suffix = get_suffix(current.tm_mday)

        # hour = current.tm_hour % 12
        # if hour == 0:
        #     hour = 12

        # am_pm = "AM"
        # if current.tm_hour / 12 >= 1:
        #     am_pm = "PM"

        # time_str = "{:d}:{:02d}:{:02d} {}".format(hour, current.tm_min, current.tm_sec, am_pm)
        # time_str = "{:d}:{:02d}:{:02d}".format(current.tm_hour, current.tm_min, current.tm_sec)
        date_str = "{}, {} {:d}{}, {:d}".format(weekday, month, current.tm_mday, suffix, current.tm_year)
        return date_str
    
    def get_time(self)-> tuple[int, int]:
        current = self.rtc.datetime
        return current.tm_hour, current.tm_min