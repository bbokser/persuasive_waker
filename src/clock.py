import adafruit_ds3231
import board
import time
# from ulab import numpy as np
import adafruit_datetime

import utils

def get_suffix(n: int):
    last_digit = n % 10
    return utils.number_suffix[last_digit]

class Clock():
    def __init__(self):
        i2c = board.I2C()  #busio.I2C(board.SCL0, board.SDA0)
        self.rtc = adafruit_ds3231.DS3231(i2c)
        self.mday = self.rtc.datetime.tm_mday
        '''
        self.rtc.datetime = time.struct_time((self.rtc.tm_year, 
                                              self.rtc.tm_mon, 
                                              self.rtc.tm_mday, 
                                              value, 
                                              self.rtc.tm_min, 
                                              self.rtc.tm_sec, 
                                              self.rtc.tm_wday, -1, -1))
        '''
    def increase_year(self):
        t0 = adafruit_datetime.datetime.fromtimestamp(time.mktime(self.rtc.datetime))
        tf = t0.replace(year=t0.year + 1)
        self.rtc.datetime = tf.timetuple()
    
    def increase_month(self):
        t0 = adafruit_datetime.datetime.fromtimestamp(time.mktime(self.rtc.datetime))
        month = t0.month + 1
        if month > 12:
            month = 1
        tf = t0.replace(month=month)
        self.rtc.datetime = tf.timetuple()
        

    def increase_day(self):
        # t0 = adafruit_datetime.datetime.fromtimestamp(time.mktime(self.rtc.datetime))
        # day = t0.day + 1
        # max_day = monthrange(t0.year, t0.month)
        # if day > max_day:
        #     day = 1
        # tf = t0.replace(day=day)
        # self.rtc.datetime = tf.timetuple()
        self.rtc.datetime = time.struct_time((self.rtc.tm_year, 
                                              self.rtc.tm_mon, 
                                              self.rtc.tm_mday+1, 
                                              self.rtc.tm_hour, 
                                              self.rtc.tm_min, 
                                              self.rtc.tm_sec, 
                                              self.rtc.tm_wday, -1, -1))

    def increase_hour(self):
        # t0 = adafruit_datetime.datetime.fromtimestamp(time.mktime(self.rtc.datetime))
        # time_change = adafruit_datetime.timedelta(hours=1)
        # tf = t0 + time_change
        # self.rtc.datetime = tf.timetuple()
        t0 = adafruit_datetime.datetime.fromtimestamp(time.mktime(self.rtc.datetime))
        hour = t0.minute + 1
        if hour > 23:
            hour = 0
        tf = t0.replace(hour=hour)
        self.rtc.datetime = tf.timetuple()

    def increase_min(self):
        t0 = adafruit_datetime.datetime.fromtimestamp(time.mktime(self.rtc.datetime))
        min = t0.minute + 1
        if min > 59:
            min = 0
        tf = t0.replace(minute=min, second=0)  # also reset seconds to zero
        self.rtc.datetime = tf.timetuple()

    def get_date_str(self)-> str:
        current = self.rtc.datetime
        weekday = utils.weekday[current.tm_wday]
        month = utils.month[current.tm_mon - 1]
        suffix = get_suffix(current.tm_mday)
        date_str = "{}, {} {:d}{}, {:d}".format(weekday, month, current.tm_mday, suffix, current.tm_year)
        return date_str
    
    def get_time_str(self)->str:
        current = self.rtc.datetime
        # hour = current.tm_hour % 12
        # if hour == 0:
        #     hour = 12

        # am_pm = "AM"
        # if current.tm_hour / 12 >= 1:
        #     am_pm = "PM"

        # time_str = "{:d}:{:02d}:{:02d} {}".format(hour, current.tm_min, current.tm_sec, am_pm)
        time_str = "{:d}:{:02d}".format(current.tm_hour, current.tm_min)
        return time_str
    
    def get_year(self)->int:
        return self.rtc.datetime.tm_year
    
    def get_month(self)->int:
        return self.rtc.datetime.tm_mon
    
    def get_day(self)->int:
        return self.rtc.datetime.tm_mday
    
    def get_hour(self)->int:
        return self.rtc.datetime.tm_hour
    
    def get_min(self)->int:
        return self.rtc.datetime.tm_min