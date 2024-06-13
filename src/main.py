import time

from fsm import FSM

# hardware
from inkdisp import InkDisp
from clock import Clock
from segment import SegmentDisp
from inputs import Inputs
from piezo import Piezo
from ir import IrSensor
import utils

filename = '/alarm.txt'

def store_alarm(hour:int, min:int, enable:bool):
    try:
        with open(filename, 'w') as file:
            file.write(str(hour) + ',' + str(min) + ',' + str(enable))
            file.flush()
    except OSError as e:
        print('Lacking permission to write to file')
        pass

def read_alarm()->dict:
    try:
        with open(filename, "r") as file:
            data = file.readline().split(',')
        output = {
            'hour': int(data[0]),
            'min': int(data[1]),
            'enable': bool(data[2])
        }
    except:
        output = {
            'hour': 8,
            'min': 0,
            'enable': False
        }
    return output

time.sleep(5)  # to ensure serial connection does not fail

# initialize class objects
fsm = FSM()
segment_disp = SegmentDisp()
clock = Clock()
inputs = Inputs()
buzzer = Piezo()
ir_sensor = IrSensor()
date_str = clock.get_date_str()
alarm_str = clock.get_alarm_str()
inkdisp = InkDisp(date_init=date_str, alarm_init=alarm_str)

dt = 0.1
blink_rate = 0.3
k_blink = int(blink_rate/dt)
k = 0
blink_bool = True
delta_max = 10  # max alarm ring time, minutes

# recall alarm time
data = read_alarm()
clock.set_alarm(hour=data['hour'], min=data['min'], enable=data['enable'])

while True:
    if k >= k_blink:
        k = 0
        blink_bool = not blink_bool
    
    button_e_val = inputs.update_button_e()
    button_b_val = inputs.update_button_b()
    state = fsm.execute(enter=button_e_val,
                        back=button_b_val,
                        set_date=inputs.get_button_d(), 
                        set_time=inputs.get_button_t(), 
                        set_alarm=inputs.get_button_a()) #,
                        #set_blinds=inputs.button_s.value)
    print('state = ', state)

    if state == 'default':
        segment_disp.print_2vals(clock.get_hour(), clock.get_min())

    elif state in ['start_set_month', 'start_set_day', 'start_set_min', 'start_set_alarm_min']:
        inputs.rezero()

    elif state == 'start_set_year':
        year = clock.get_year()
        month = clock.get_month()
        day = clock.get_day()
        inputs.rezero()
    elif state == 'set_year':
        year_new = utils.wrap_to_range(year + inputs.get_encoder_pos(), a=-999, b=9999)
        segment_disp.print(year_new, blink_bool)
    elif state == 'set_month':
        month_new = utils.wrap_to_range(month + inputs.get_encoder_pos(), a=1, b=12)
        segment_disp.print_2vals(month_new, day, wink_left=blink_bool)
    elif state == 'set_day':
        day_max = utils.get_max_day(year=year_new, month=month_new)
        day_new = utils.wrap_to_range(day + inputs.get_encoder_pos(), a=1, b=day_max)
        segment_disp.print_2vals(month_new, day_new, wink_right=blink_bool)
    elif state == 'end_set_day':
        clock.set_date(year=year_new, month=month_new, day=day_new)

    elif state == 'start_set_hour':
        hour = clock.get_hour()
        minute = clock.get_min()
        inputs.rezero()
    elif state == 'set_hour':
        hour_new = (hour + inputs.get_encoder_pos()) % 24
        segment_disp.print_2vals(hour_new, minute, wink_left=blink_bool)
    elif state == 'set_min':
        min_new = (minute + inputs.get_encoder_pos()) % 60
        segment_disp.print_2vals(hour_new, min_new, wink_right=blink_bool)
    elif state == 'end_set_min':
        clock.set_time(hour=hour_new, min=min_new)
    
    elif state == 'start_set_alarm':
        hour = clock.get_alarm_hour()
        minute = clock.get_alarm_min()
        inputs.rezero()
    elif state == 'set_alarm_hour':
        hour_new = (hour + inputs.get_encoder_pos()) % 24
        segment_disp.print_2vals(hour_new, minute, wink_left=blink_bool)
    elif state == 'set_alarm_min':
        min_new = (minute + inputs.get_encoder_pos()) % 60
        segment_disp.print_2vals(hour_new, min_new, wink_right=blink_bool)
    elif state == 'end_set_alarm_min':
        clock.set_alarm(hour=hour_new, min=min_new)
        store_alarm(hour_new, min_new, True)

    elif state == 'set_no_alarm':
        clock.alarm_enable = False
        store_alarm(hour, minute, False)

    if date_str != clock.get_date_str() or alarm_str != clock.get_alarm_str():
        date_str = clock.get_date_str()
        alarm_str = clock.get_alarm_str()
        inkdisp.clear()
        inkdisp.apply_info(date=date_str, alarm=alarm_str)
        inkdisp.update()
    
    if clock.alarm_enable is True and clock.alarm_temp_disable is False:
        delta = clock.get_alarm_delta()
        if -delta_max < delta <= 0:
            if ir_sensor.check_ir() is True:
                clock.alarm_temp_disable = True
            magnitude = abs(delta/delta_max)
            amp = utils.clip(magnitude, 0.1, 1.)
            tone = utils.translate(magnitude, 262, 464)
            buzzer.play(tone=tone, amp=amp, on=blink_bool)
        else:
            buzzer.shutoff()
    
    elif clock.alarm_enable is True and clock.alarm_temp_disable is True:
        buzzer.shutoff()
        if delta < -delta_max:
            clock.alarm_temp_disable = False
    else:
        buzzer.shutoff()

    k += 1
    time.sleep(dt)
