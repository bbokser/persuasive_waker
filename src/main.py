import time
import board
import busio

from fsm import FSM
import utils

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

# initialize class objects
i2c = busio.I2C(scl=board.GP5, sda=board.GP4)
as1115 = AS1115(i2c)
clock = Clock(i2c)
rf = PinButton(board.GP15)
enc_button = ScanButton()
battery = Batt(pin_vbatt=board.VOLTAGE_MONITOR, pin_usb=board.VBUS_SENSE)
encoder = Encoder(pinA=board.GP1, pinB=board.GP0)
buzzer = Piezo(board.GP2)
sensor = HTSensor(i2c, address=0x45)
seg_colon = LED(board.GP13)  # segment display colon
seg_apost = LED(board.GP12)  # segment display apostrophe
seg_colon.on()
seg_colon.set_brightness(0.5)

temp_str = sensor.get_temperature()
humidity_str = sensor.get_humidity()
date_str = clock.get_date_str()
alarm_str = clock.get_alarm_str()
inkdisp = InkDisp(
    cs=board.GP21,
    dc=board.GP22,
    reset=board.GP17,
    date_init=date_str,
    alarm_init=alarm_str,
    temp_init=temp_str,
    humidity_init=humidity_str,
    batt_init=battery.get_batt_frac(),
    usb_init=battery.usb_power.value,
)
clock.set_refresh()

dt = 0.1
beat_rate = 0.3
k_beat = int(beat_rate / dt)
k = 0
heartbeat = True

fsm = FSM()

while True:
    if k >= k_beat:
        k = 0
        heartbeat = not heartbeat

    buttons = as1115.scan_keys()

    rf_input = rf.update()
    # buttons physical order
    # 3, 4, 5, 6, 2, 1, 0
    state = fsm.execute(
        enter=enc_button.update(buttons[7]),
        back=buttons[3],
        set_date=buttons[4],
        set_time=buttons[5],
        set_alarm=buttons[6],
        set_brightness=buttons[2],
        alarm_status=clock.get_alarm_status(rf_input),
    )
    print("state = ", state)

    if state == "default":
        seg_colon.on()
        as1115.display_hourmin(clock.get_hour(), clock.get_min())
    elif state in [
        "start_set_month",
        "start_set_day",
        "start_set_min",
        "start_set_alarm_min",
    ]:
        encoder.rezero()

    elif state == "start_set_year":
        seg_colon.off()
        year = clock.get_year()
        month = clock.get_month()
        day = clock.get_day()
        encoder.rezero()
    elif state == "set_year":
        year_new = utils.wrap_to_range(year + encoder.get_encoder_pos(), a=1970, b=2037)
        as1115.display_int(year_new)
        as1115.wink_left(heartbeat)
        as1115.wink_right(heartbeat)
    elif state == "set_month":
        month_new = utils.wrap_to_range(month + encoder.get_encoder_pos(), a=1, b=12)
        as1115.display_hourmin(month_new, day)
        as1115.wink_left(heartbeat)
    elif state == "set_day":
        day_max = utils.get_max_day(year=year_new, month=month_new)
        day_new = utils.wrap_to_range(day + encoder.get_encoder_pos(), a=1, b=day_max)
        as1115.display_hourmin(month_new, day_new)
        as1115.wink_right(heartbeat)
    elif state == "end_set_day":
        clock.set_date(year=year_new, month=month_new, day=day_new)
        as1115.unwink()

    elif state == "start_set_hour":
        hour = clock.get_hour()
        minute = clock.get_min()
        encoder.rezero()
    elif state == "set_hour":
        hour_new = (hour + encoder.get_encoder_pos()) % 24
        as1115.display_hourmin(hour_new, minute)
        as1115.wink_left(heartbeat)
    elif state == "set_min":
        min_new = (minute + encoder.get_encoder_pos()) % 60
        as1115.display_hourmin(hour_new, min_new)
        as1115.wink_right(heartbeat)
    elif state == "end_set_min":
        clock.set_time(hour=hour_new, min=min_new)
        as1115.unwink()

    elif state == "start_set_alarm":
        hour = clock.get_alarm_hour()
        minute = clock.get_alarm_min()
        encoder.rezero()
    elif state == "set_alarm_hour":
        hour_new = (hour + encoder.get_encoder_pos()) % 24
        as1115.display_hourmin(hour_new, minute)
        as1115.wink_left(heartbeat)
    elif state == "set_alarm_min":
        min_new = (minute + encoder.get_encoder_pos()) % 60
        as1115.display_hourmin(hour_new, min_new)
        as1115.wink_right(heartbeat)
    elif state == "end_set_alarm_min":
        clock.set_alarm(hour=hour_new, min=min_new)
        as1115.unwink()

    elif state == "set_no_alarm":
        clock.disable_alarm()

    elif state == "start_set_brightness":
        seg_colon.off()
        encoder.rezero()
        brightness_new = as1115.brightness
    elif state == "set_brightness":
        as1115.brightness = (brightness_new + encoder.get_encoder_pos()) % 8
        as1115.display_int(as1115.brightness)
        seg_colon.set_brightness(as1115.brightness / 15)
        seg_apost.set_brightness(as1115.brightness / 15)
    elif state == "end_set_brightness":
        pass

    elif state == "alarming":
        rf.update()
        as1115.display_hourmin(clock.get_hour(), clock.get_min())
        alarm_delta = clock.get_alarm_delta()
        magnitude = utils.clip(abs(alarm_delta / clock.alarm_delta_max), 0.1, 1.0)
        tone = 200  # utils.translate(utils.clip(magnitude, 0.1, 1.), 262, 464)
        buzzer.play(tone=tone, amp=magnitude, on=heartbeat)
    elif state == "end_alarming":
        clock.reset_alarm()
        buzzer.shutoff()

    # refresh inkdisp, make sure at least 3 minutes have passed before you refresh again
    if (
        date_str != clock.get_date_str() or alarm_str != clock.get_alarm_str()
    ) and clock.get_refresh_delta() > 180:
        date_str = clock.get_date_str()
        alarm_str = clock.get_alarm_str()
        temp_str = sensor.get_temperature()
        humidity_str = sensor.get_humidity()
        inkdisp.clear()
        inkdisp.apply_info(
            date=date_str,
            alarm=alarm_str,
            temp=temp_str,
            humidity=humidity_str,
            batt=battery.get_batt_frac(),
            usb=battery.usb_power.value,
        )
        inkdisp.update()
        clock.set_refresh()

    k += 1
    time.sleep(dt)
