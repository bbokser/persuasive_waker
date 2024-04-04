import adafruit_ds3231
import board
import time
# from ulab import numpy as np
# import adafruit_datetime

import utils

def get_suffix(n: int):
    last_digit = n % 10
    return utils.number_suffix[last_digit]

def leapyear(year:int)->bool:
    # check whether a given year is a leap year.
    '''
    https://www.rmg.co.uk/stories/topics/which-years-are-leap-years-can-you-have-leap-seconds
    "To be a leap year, the year number must be divisible by four
    except for end-of-century years, which must be divisible by 400"
    '''
    if (year % 4) != 0:
        # years not divisible by 4 are not leap years
        return False
    if (year % 100) != 0:
        # years divisible by 4 but not 100 are leap years
        return True
    if (year % 400) != 0:
        # years divisible by 4 and 100 but not 400 are not leap years
        return False
    return True

def get_max_day(year:int, month:int)->int:
    # return the number of days in the given month and for the given year
    # https://stackoverflow.com/questions/28800127/universal-formula-to-calculate-the-number-of-days-in-a-month-taking-into-account
    return 28 + (month + (month/8)) % 2 + 2 % month + 2 * (1/month) + ((month == 2) * leapyear(year))
    
class Clock():
    def __init__(self):
        i2c = board.I2C()  #busio.I2C(board.SCL0, board.SDA0)
        self.rtc = adafruit_ds3231.DS3231(i2c)
        
    def set_date(self, year:int, month:int, day:int):
        self.rtc.datetime = time.struct_time((year, 
                                              month, 
                                              day, 
                                              self.rtc.tm_hour, 
                                              self.rtc.tm_min, 
                                              self.rtc.tm_sec, 
                                              self.rtc.tm_wday, -1, -1))

    def set_time(self, hour:int, min:int):
        self.rtc.datetime = time.struct_time((self.rtc.tm_year, 
                                              self.rtc.tm_mon, 
                                              self.rtc.tm_mday, 
                                              hour, 
                                              min, 
                                              0, 
                                              self.rtc.tm_wday, -1, -1))

    def get_date_str(self)-> str:
        current = self.rtc.datetime
        weekday = utils.weekday[current.tm_wday]
        month = utils.month[current.tm_mon - 1]
        suffix = get_suffix(current.tm_mday)
        date_str = "{}, {} {:d}{}, {:d}".format(weekday, month, current.tm_mday, suffix, current.tm_year)
        return date_str
    
    def get_time_str(self)->str:
        current = self.rtc.datetime
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
    
