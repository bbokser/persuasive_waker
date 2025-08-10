import time
import board
import busio

from fsm import FSM

# hardware
from batt import Batt
from inkdisp import InkDisp
from clock import Clock
from as1115 import AS1115
from encoder import Encoder
from buzzer import Buzzer
from button import PinButton, ScanButton
from sense_ht import HTSensor
from led import LED

# time.sleep(5)  # to ensure serial connection does not fail


class OS(FSM):
    def __init__(self, verbose):
        # initialize class objects
        brightness_init = 2
        i2c = busio.I2C(scl=board.GP5, sda=board.GP4)
        self.as1115 = AS1115(i2c, brightness=brightness_init)
        self.clock = Clock(i2c)
        # this has to run after clock is created
        super().__init__(verbose=verbose)
        # disable the alarms on reset because I haven't figured out how to retrieve the saved info from the rtc
        self.clock.alarm1.disable()
        self.clock.alarm2.disable()
        self.rf = PinButton(board.GP15)
        self.enc_button = ScanButton()
        self.alarm_button = ScanButton()
        self.opt_button = ScanButton()
        self.battery = Batt(pin_vbatt=board.VOLTAGE_MONITOR, pin_usb=board.VBUS_SENSE)
        self.encoder = Encoder(pinA=board.GP1, pinB=board.GP0)
        self.buzzer = Buzzer(board.GP2)
        self.sensor = HTSensor(i2c, address=0x45, units=0)
        # segment display colon
        self.seg_colon = LED(board.GP13, brightness_init / 15)
        self.seg_colon.on()
        # segment display apostrophe
        self.seg_apost = LED(board.GP12, brightness_init / 15)

        self.inkdisp = InkDisp(cs=board.GP21, dc=board.GP22, reset=board.GP17)
        self.update_disp()

        # 24 vs 12 hour format
        self.format = 0
        self.format_new = 0

        self.wday_idx = 0
        self.wday_set_new = [0] * 7
        self.dt = 0.1
        self.beat_rate = 0.3  # should be a multiple of dt

    def run(self):
        z = 0
        k = 0
        self.heartbeat = True
        k_beat = int(self.beat_rate / self.dt)

        j = 0
        # how many seconds before refresh
        refresh_time = 10 * 60
        refresh_counter = int(refresh_time / self.dt)
        # reheat the sensor chip once per day
        reheat_counter = int(24 * 60 * 60 / refresh_time)
        self.power_value_prev = self.battery.usb_power.value

        while True:
            if k >= k_beat:
                k = 0
                self.heartbeat = not self.heartbeat

            # buttons register-physical-symbol order
            # 5-S4-date, 4-S5-time, 6-S3-alarm, 3-S6-light, 1-S7-gear, 0-S8-back, 7-Enc-Enter
            buttons = self.as1115.scan_keys()
            self.b_back = buttons[0]
            self.b_options = self.opt_button.update(buttons[1])
            self.b_set_brightness = buttons[2]
            self.b_set_time = buttons[4]
            self.b_set_date = buttons[5]
            self.b_set_alarm = self.alarm_button.update(buttons[6])
            self.b_enter = self.enc_button.update(buttons[7])

            self.execute()

            # refresh inkdisp, make sure at least 3 minutes have passed before you refresh again
            if j > refresh_counter:
                if z == 0:
                    self.sensor.set_mode_read()
                j = 0
                self.update_disp()
                z += 1
                if z > reheat_counter:
                    self.sensor.set_mode_heat()
                    z = 0

            power_value = self.battery.usb_power.value
            # warning light for being unplugged
            if power_value is False:
                self.seg_apost.blink(self.heartbeat)

            if self.power_value_prev != power_value:
                self.update_disp()
                if power_value is True:
                    self.seg_apost.off()

            self.power_value_prev = power_value

            k += 1
            j += 1
            time.sleep(self.dt)

    def update_disp(self):
        disp_info = {
            "weekday": self.clock.get_weekday_str(),
            "month": self.clock.get_month_str(),
            "day": self.clock.get_day_str(),
            "year": self.clock.get_year_str(),
            "alarm1": self.clock.alarm1.get_str(),
            "alarm1wdays": self.clock.alarm1.get_wday_set_str(),
            "alarm2": self.clock.alarm2.get_str(),
            "alarm2wdays": self.clock.alarm2.get_wday_set_str(),
            "temp": self.sensor.get_temperature(),
            "humidity": self.sensor.get_humidity(),
            "batt": self.battery.get_batt_frac(),
            "usb": self.battery.usb_power.value,
            "meridiem": self.clock.get_meridiem_str(),
        }
        self.inkdisp.clear()
        self.inkdisp.apply_info(disp_info)
        self.inkdisp.update()


if __name__ == "__main__":
    verbose = True
    os = OS(verbose)
    os.run()
