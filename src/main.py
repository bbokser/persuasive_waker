import time

from fsm import FSM

# hardware
from inkdisp import InkDisp
from clock import Clock
from segment import SegmentDisp
from inputs import Inputs
from piezo import Piezo

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

def wrap_to_range(x:int, a:int, b:int)->int:
    '''
    x: the value to wrap
    a <= x <= b
    '''
    return int((x - a) % (b - a + 1) + a)

time.sleep(5)  # to ensure serial connection does not fail

# initialize class objects
fsm = FSM()
segment_disp = SegmentDisp()
clock = Clock()
inputs = Inputs()
buzzer = Piezo()
date_str = clock.get_date_str()
alarm_str = clock.get_alarm_str()
inkdisp = InkDisp(date_init=date_str, alarm_init=alarm_str)

dt = 0.1
blink_rate = 0.3
k_blink = int(blink_rate/dt)
k = 0
blink_bool = True
delta_max = 30  # max alarm ring time

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
        year_new = wrap_to_range(year + inputs.get_encoder_pos(), a=-999, b=9999)
        segment_disp.print(year_new, blink_bool)
    elif state == 'set_month':
        month_new = wrap_to_range(month + inputs.get_encoder_pos(), a=1, b=12)
        segment_disp.print_2vals(month_new, day, wink_left=blink_bool)
    elif state == 'set_day':
        day_max = get_max_day(year=year_new, month=month_new)
        day_new = wrap_to_range(day + inputs.get_encoder_pos(), a=1, b=day_max)
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
    elif state == 'set_no_alarm':
        clock.alarm_nullify = True
        # clock.set_alarm(hour=hour_new, min=min_new, nullify=True)

    if date_str != clock.get_date_str() or alarm_str != clock.get_alarm_str():
        date_str = clock.get_date_str()
        alarm_str = clock.get_alarm_str()
        inkdisp.clear()
        inkdisp.apply_info(date=date_str, alarm=alarm_str)
        inkdisp.update()
    
    if clock.alarm_nullify is False:
        delta = clock.get_alarm_delta()
        if -delta_max < delta <= 0:
            buzzer.play(note='c4', amp=abs(delta/delta_max), on=blink_bool)
        else:
            buzzer.shutoff()

    k += 1
    time.sleep(dt)
