import adafruit_ds3231
import time
# from ulab import numpy as np
import adafruit_datetime
from busio import I2C
import utils

def get_suffix(n: int):
    if 10 < n < 14:
        return 'th'
    else:
        last_digit = n % 10
        return utils.number_suffix[last_digit]
    
class Clock():
    def __init__(self, i2c: I2C):
        self.rtc = adafruit_ds3231.DS3231(i2c)
        self.alarm_enable = False
        self.datetime_refresh = self.get_datetime_now()
        
    def set_date(self, year:int, month:int, day:int):
        year = utils.clip(year, 1970, 2037)  # duct-tape Y2038 problem
        self.rtc.datetime = time.struct_time((year, 
                                              month, 
                                              day, 
                                              self.rtc.datetime.tm_hour, 
                                              self.rtc.datetime.tm_min, 
                                              self.rtc.datetime.tm_sec, 
                                              self.rtc.datetime.tm_wday, -1, -1))
        # prevents premature refresh due to time confusion
        self.datetime_refresh = self.get_datetime_now()

    def set_time(self, hour:int, min:int):
        self.rtc.datetime = time.struct_time((self.rtc.datetime.tm_year, 
                                              self.rtc.datetime.tm_mon, 
                                              self.rtc.datetime.tm_mday, 
                                              hour, 
                                              min, 
                                              0, 
                                              self.rtc.datetime.tm_wday, -1, -1))
        self.datetime_refresh = self.get_datetime_now()

    def get_date_str(self)-> str:
        current = self.rtc.datetime
        weekday = utils.weekday[current.tm_wday]
        month = utils.month[current.tm_mon - 1]
        suffix = get_suffix(current.tm_mday)
        date_str = '{}, {} {:d}{}, {:d}'.format(weekday, month, current.tm_mday, suffix, current.tm_year)
        return date_str
    
    def get_time_str(self)->str:
        current = self.rtc.datetime
        return '{:d}:{:02d}'.format(current.tm_hour, current.tm_min)

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
    
    # alarm functions
    def set_alarm(self, hour:int, min:int, enable=True):
        self.rtc.alarm1 = (time.struct_time((self.rtc.datetime.tm_year, 
                                              self.rtc.datetime.tm_mon, 
                                              self.rtc.datetime.tm_mday, 
                                              hour, 
                                              min, 
                                              0, 
                                              self.rtc.datetime.tm_wday, -1, -1)), "daily")
        self.alarm_enable = enable

    def get_alarm_status(self)->bool:
        return self.rtc.alarm1_status
    
    def reset_alarm(self)->None:
        self.rtc.alarm1_status = False

    def disable_alarm(self)->None:
        self.alarm_enable = False
        
    def get_alarm_hour(self)->int:
        alarm_time, _ = self.rtc.alarm1
        return alarm_time.tm_hour
    
    def get_alarm_min(self)->int:
        alarm_time, _ = self.rtc.alarm1
        return alarm_time.tm_min
    
    def get_alarm_str(self)->str:
        if self.alarm_enable is True:
            return '{:d}:{:02d}'.format(self.get_alarm_hour(), self.get_alarm_min())
        else:
            return 'None'
    
    def get_alarm_t(self)->adafruit_datetime.date:
        # get time of next alarm
        t = self.get_datetime_now()
        return t.replace(hour=self.get_alarm_hour(), minute=self.get_alarm_hour())

    def get_datetime_now(self)->adafruit_datetime.date:
        return adafruit_datetime.datetime.fromtimestamp(time.mktime(self.rtc.datetime))
    
    def get_delta(self, t_then:adafruit_datetime.date)->float:
         # get difference between now and a specified time
        # https://stackoverflow.com/questions/3096953/how-to-calculate-the-time-interval-between-two-time-strings
        # if then is in the future, result is positive
        # if then is in the past, result is negative
        t_delta = self.get_datetime_now() - t_then
        return t_delta.total_seconds()  # time delta in seconds
    
    def get_alarm_delta(self)->float:
        # get time until next alarm
        return self.get_delta(self.get_alarm_t())
    
    def get_refresh_delta(self)->float:
        # get time since last refresh
        return self.get_delta(self.datetime_refresh)
    
    def set_refresh(self):
        self.datetime_refresh = self.get_datetime_now()

    
