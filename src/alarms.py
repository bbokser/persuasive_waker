import adafruit_datetime
import time

wday_sets = [
    set((0, 1, 2, 3, 4, 5, 6)),  # full week
    set((1, 2, 3, 4, 5)),  # mon-fri
    set((0, 6)),  # sat & sun
]

wday_set_lbls = [
    "",
    " M-F",
    " S&S",
]


class Alarm:
    def __init__(self, rtc, idx):
        self.rtc = rtc
        self.idx = idx

        self.wday_set = 0  # corresponds to full week
        self.start_day = None
        self.enable = False
        self.delta_max = 10 * 60  # max alarm ring time, seconds

    def log_start(self) -> None:
        # remembering date prevents, say, the alarm ringing for only one minute if it's set to 23:59
        self.start_day = self.rtc.datetime.tm_mday

    def reset(self) -> None:
        if self.idx == 0:
            self.rtc.alarm1_status = False
        else:
            self.rtc.alarm2_status = False
        self.start_day = None

    def disable(self) -> None:
        self.enable = False

    def get_hour(self) -> int:
        if self.idx == 0:
            time, _ = self.rtc.alarm1
        else:
            time, _ = self.rtc.alarm2
        return time.tm_hour

    def get_min(self) -> int:
        if self.idx == 0:
            time, _ = self.rtc.alarm1
        else:
            time, _ = self.rtc.alarm2
        return time.tm_min

    def get_str(self) -> str:
        if self.enable is True:
            return (
                "{:d}:{:02d}".format(self.get_hour(), self.get_min())
                + wday_set_lbls[self.wday_set]
            )
        else:
            return "None"

    def get_status_init(self) -> bool:
        """
        Get permission to enter the alarming state.
        Only check wday on entering in case alarm starts at 23:59 or some shit
        """
        if self.idx == 0:
            chip_status = self.rtc.alarm1_status
        else:
            chip_status = self.rtc.alarm2_status

        wday = self.rtc.datetime.tm_wday
        if self.enable and chip_status and (wday in wday_sets[self.wday_set]):
            delta = self.get_alarm_delta()
            if 0 <= delta <= self.delta_max:
                final_status = True
            else:
                self.reset()
                final_status = False
        else:
            final_status = False
        return final_status

    def get_status(self, cancel: bool) -> bool:
        """
        Get permission to continue alarming
        A large number of criteria must be reached for the alarm to
        really, truly be allowed to sound
        """
        if self.idx == 0:
            chip_status = self.rtc.alarm1_status
        else:
            chip_status = self.rtc.alarm2_status

        if self.enable and chip_status and not cancel:
            delta = self.get_alarm_delta()
            if 0 <= delta <= self.delta_max:
                final_status = True
            else:
                self.reset()
                final_status = False
        else:
            final_status = False
        return final_status

    def set_alarm(self, hour: int, min: int, wday_set: int = 0, enable: bool = True):
        time_struct = (
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
        if self.idx == 0:
            self.rtc.alarm1 = time_struct
        else:
            self.rtc.alarm2 = time_struct
        self.wday_set = wday_set
        self.enable = enable

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

    def get_datetime_alarm(self) -> adafruit_datetime.datetime:
        # get time of next alarm
        t = self.get_datetime_now()
        hour = self.get_hour()
        minute = self.get_min()
        if self.start_day is not None:
            return t.replace(day=self.start_day, hour=hour, minute=minute, second=0)
        else:
            return t.replace(hour=hour, minute=minute, second=0)
