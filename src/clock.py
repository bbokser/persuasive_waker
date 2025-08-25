import adafruit_ds3231
import time
import adafruit_datetime
from busio import I2C
import utils

from alarms import Alarm


def get_suffix(n: int):
    if 10 < n < 14:
        return "th"
    else:
        last_digit = n % 10
        return utils.number_suffix[last_digit]


class Clock:
    def __init__(self, i2c: I2C):
        self.rtc = adafruit_ds3231.DS3231(i2c)
        self.alarm1 = Alarm(rtc=self.rtc, idx=0)
        self.alarm2 = Alarm(rtc=self.rtc, idx=1)
        self.get_meridiem_str = self.get_meridiem_str_24hr

    def set_date(self, year: int, month: int, day: int):
        year = utils.clip(year, 1970, 2037)  # duct-tape Y2038 problem
        wday = adafruit_datetime.date(year, month, day).weekday()
        self.rtc.datetime = time.struct_time(
            (
                year,
                month,
                day,
                self.rtc.datetime.tm_hour,
                self.rtc.datetime.tm_min,
                self.rtc.datetime.tm_sec,
                wday,
                -1,
                -1,
            )
        )

    def set_time(self, hour: int, min: int):
        self.rtc.datetime = time.struct_time(
            (
                self.rtc.datetime.tm_year,
                self.rtc.datetime.tm_mon,
                self.rtc.datetime.tm_mday,
                hour,
                min,
                0,
                self.rtc.datetime.tm_wday,
                -1,
                -1,
            )
        )

    def get_weekday_str(self) -> str:
        return utils.weekday[self.rtc.datetime.tm_wday]

    def get_month_str(self) -> str:
        return utils.month[self.rtc.datetime.tm_mon - 1]

    def get_day_str(self) -> str:
        current = self.rtc.datetime
        suffix = get_suffix(current.tm_mday)
        day_str = "{:d}{}".format(current.tm_mday, suffix)
        return day_str

    def get_year_str(self) -> str:
        return "{:d}".format(self.rtc.datetime.tm_year)

    def get_time_str(self) -> str:
        current = self.rtc.datetime
        return "{:d}:{:02d}".format(current.tm_hour, current.tm_min)

    def get_year(self) -> int:
        return self.rtc.datetime.tm_year

    def get_month(self) -> int:
        return self.rtc.datetime.tm_mon

    def get_day(self) -> int:
        return self.rtc.datetime.tm_mday

    def get_hour(self) -> int:
        return self.rtc.datetime.tm_hour

    def get_min(self) -> int:
        return self.rtc.datetime.tm_min

    def get_delta_hours(self, t_then: float) -> float:
        """
        get difference between now and a specified time of day in units of hours
        - if then is in the future, result is negative
        - if then is in the past, result is positive
        - does not cross midnight
        """
        t_now = self.get_hour() + self.get_min() / 60
        return t_now - t_then

    def get_meridiem_str_24hr(self) -> str:
        return ""

    def get_meridiem_str_12hr(self) -> str:
        hour = self.get_hour()
        if hour > 12:
            return "PM"
        else:
            return "AM"

    def change_format(self, format) -> None:
        if format == 0:
            self.get_meridiem_str = self.get_meridiem_str_24hr
        else:
            self.get_meridiem_str = self.get_meridiem_str_12hr
