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
from piezo import Piezo
from button import PinButton, ScanButton
from sense_ht import HTSensor
from led import LED

# time.sleep(5)  # to ensure serial connection does not fail


class OS(FSM):
    def __init__(self, verbose):
        super().__init__(verbose=verbose)
        # initialize class objects
        brightness_init = 2
        i2c = busio.I2C(scl=board.GP5, sda=board.GP4)
        self.as1115 = AS1115(i2c, brightness=brightness_init)
        self.clock = Clock(i2c)
        self.rf = PinButton(board.GP15)
        self.enc_button = ScanButton()
        self.alarm_button = ScanButton()
        self.battery = Batt(pin_vbatt=board.VOLTAGE_MONITOR, pin_usb=board.VBUS_SENSE)
        self.encoder = Encoder(pinA=board.GP1, pinB=board.GP0)
        self.buzzer = Piezo(board.GP2)
        self.sensor = HTSensor(i2c, address=0x45)
        # segment display colon
        self.seg_colon = LED(board.GP13, brightness_init / 15)
        self.seg_colon.on()
        # segment display apostrophe
        self.seg_apost = LED(board.GP12, brightness_init / 15)

        self.inkdisp = InkDisp(cs=board.GP21, dc=board.GP22, reset=board.GP17)
        self.inkdisp.apply_info(self.get_disp_info())
        self.inkdisp.update()

        self.dt = 0.1
        self.beat_rate = 0.3

    def run(self):
        k = 0
        self.heartbeat = True
        k_beat = int(self.beat_rate / self.dt)

        j = 0
        refresh_counter = int(180 / self.dt)

        i = 0
        heater_counter = int(3600 / self.dt)

        disp_info = self.get_disp_info()
        while True:
            if k >= k_beat:
                k = 0
                self.heartbeat = not self.heartbeat

            # buttons register-physical-symbol order
            # 5-S4-date, 4-S5-time, 6-S3-alarm, 3-S6-light, 1-S7-gear, 0-S8-back, 7-Enc-Enter
            buttons = self.as1115.scan_keys()
            self.b_back = buttons[0]
            self.b_options = buttons[1]
            self.b_set_brightness = buttons[2]
            self.b_set_time = buttons[4]
            self.b_set_date = buttons[5]
            self.b_set_alarm = self.alarm_button.update(buttons[6])
            self.b_enter = self.enc_button.update(buttons[7])

            self.execute()

            # refresh inkdisp, make sure at least 3 minutes have passed before you refresh again
            if j > refresh_counter:
                j = 0
                if disp_info != self.get_disp_info():
                    disp_info = self.get_disp_info()
                    self.inkdisp.clear()
                    self.inkdisp.apply_info(disp_info)
                    self.inkdisp.update()

            if i > heater_counter:
                i = 0
                self.sensor.set_mode_heat()

            # warning light for being unplugged
            if self.battery.usb_power.value is False:
                self.seg_apost.blink(self.heartbeat)
            else:
                self.seg_apost.off()

            k += 1
            j += 1
            i += 1
            time.sleep(self.dt)

    def get_disp_info(self):
        disp_info = {
            "weekday": self.clock.get_weekday_str(),
            "month": self.clock.get_month_str(),
            "day": self.clock.get_day_str(),
            "year": self.clock.get_year_str(),
            "alarm1": self.clock.alarm1.get_str(),
            "alarm2": self.clock.alarm2.get_str(),
            "temp": self.sensor.get_temperature(),
            "humidity": self.sensor.get_humidity(),
            "batt": self.battery.get_batt_frac(),
            "usb": self.battery.usb_power.value,
        }
        return disp_info


if __name__ == "__main__":
    verbose = True
    os = OS(verbose)
    os.run()
