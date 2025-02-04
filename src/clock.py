import adafruit_ds3231
import time

# from ulab import numpy as np
import adafruit_datetime
from busio import I2C
import utils


def get_suffix(n: int):
    if 10 < n < 14:
        return "th"
    else:
        last_digit = n % 10
        return utils.number_suffix[last_digit]


class Clock:
    def __init__(self, i2c: I2C):
        self.rtc = adafruit_ds3231.DS3231(i2c)
        self.alarm_start_day = None
        self.alarm_enable = False
        self.alarm_minutes = 10  # max alarm ring time
        self.alarm_delta_max = self.alarm_minutes * 60  # max alarm ring time, seconds

    def set_date(self, year: int, month: int, day: int):
        year = utils.clip(year, 1970, 2037)  # duct-tape Y2038 problem
        wday = utils.get_wday(year, month, day)
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

    # alarm functions
    def set_alarm(self, hour: int, min: int, enable=True):
        self.rtc.alarm1 = (
            time.struct_time(
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
            ),
            "daily",
        )
        self.alarm_enable = enable

    def get_alarm_status(self, cancel: bool) -> bool:
        """
        A large number of criteria must be reached for the alarm to
        really, truly be allowed to sound
        """
        if self.alarm_enable and self.rtc.alarm1_status and not cancel:
            alarm_delta = self.get_alarm_delta()
            if 0 <= alarm_delta <= self.alarm_delta_max:
                alarm_status = True
            else:
                self.reset_alarm()
                alarm_status = False
        else:
            alarm_status = False
        return alarm_status

    def log_alarm_start(self) -> None:
        # remembering date prevents, say, the alarm ringing for only one minute if it's set to 23:59
        self.alarm_start_day = self.rtc.datetime.tm_mday

    def reset_alarm(self) -> None:
        self.rtc.alarm1_status = False
        self.alarm_start_day = None

    def disable_alarm(self) -> None:
        self.alarm_enable = False

    def get_alarm_hour(self) -> int:
        alarm_time, _ = self.rtc.alarm1
        return alarm_time.tm_hour

    def get_alarm_min(self) -> int:
        alarm_time, _ = self.rtc.alarm1
        return alarm_time.tm_min

    def get_alarm_str(self) -> str:
        if self.alarm_enable is True:
            return "{:d}:{:02d}".format(self.get_alarm_hour(), self.get_alarm_min())
        else:
            return "None"

    def get_datetime_alarm(self) -> adafruit_datetime.datetime:
        # get time of next alarm
        t = self.get_datetime_now()
        hour = self.get_alarm_hour()
        minute = self.get_alarm_min()
        if self.alarm_start_day is not None:
            return t.replace(
                day=self.alarm_start_day, hour=hour, minute=minute, second=0
            )
        else:
            return t.replace(hour=hour, minute=minute, second=0)

    def get_datetime_now(self) -> adafruit_datetime.datetime:
        return adafruit_datetime.datetime.fromtimestamp(time.mktime(self.rtc.datetime))

    def get_delta(self, t_then: adafruit_datetime.date) -> float:
        # get difference between now and a specified time
        # https://stackoverflow.com/questions/3096953/how-to-calculate-the-time-interval-between-two-time-strings
        # if then is in the future, result is negative
        # if then is in the past, result is positive
        t_delta = self.get_datetime_now() - t_then
        return t_delta.total_seconds()  # time delta in seconds

    def get_alarm_delta(self) -> float:
        # get time until next alarm
        return self.get_delta(self.get_datetime_alarm())
