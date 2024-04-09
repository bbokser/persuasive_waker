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

def wrap_to_range(x:int, a:int, b:int):
    '''
    x: the value to wrap
    a <= x <= b
    '''
    return (x - a) % (b - a + 1) + a

def fullblink(value, blink_bool):
    # provide full display blink
    if blink_bool is True:
        return '    '
    return value

def halfblink(value, blink_bool):
    # provide half of display blink
    if blink_bool is True:
        return '  '
    return value

time.sleep(5)  # to ensure serial connection does not fail

# initialize class objects
fsm = FSM()
segment_disp = SegmentDisp()
clock = Clock()
inputs = Inputs()
piezo = Piezo()
date_str = clock.get_date_str()
alarm_str = clock.get_alarm_str()
inkdisp = InkDisp(date_init=date_str, alarm_init=alarm_str)

dt = 0.1
blink_rate = 0.5
k_blink = int(blink_rate/dt)
k = 0
blink_bool = 1

while True:
    if k >= k_blink:
        k = 0
        blink_bool *= -1
    
    state = fsm.execute(set_date=inputs.d, 
                        set_time=inputs.t, 
                        set_alarm=inputs.a,
                        set_blinds=inputs.b)
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
        segment_disp.print(fullblink(year_new, blink_bool))
    elif state == 'set_month':
        month_new = wrap_to_range(month + inputs.get_encoder_pos(), a=1, b=12)
        segment_disp.print_2vals(halfblink(month_new, blink_bool), day)
    elif state == 'set_day':
        day_max = get_max_day(year=year_new, month=month_new)
        day_new = wrap_to_range(day + inputs.get_encoder_pos(), a=1, b=day_max)
        segment_disp.print_2vals(month_new, halfblink(day_new, blink_bool))
    elif state == 'end_set_day':
        clock.set_date(year=year_new, month=month_new, day=day_new)

    elif state == 'start_set_hour':
        hour = clock.get_hour()
        minute = clock.get_min()
        inputs.rezero()
    elif state == 'set_hour':
        hour_new = (hour + inputs.get_encoder_pos()) % 24
        segment_disp.print_2vals(halfblink(hour_new, blink_bool), minute)
    elif state == 'set_min':
        min_new = (minute + inputs.get_encoder_pos()) % 60
        segment_disp.print_2vals(hour_new, halfblink(min_new, blink_bool))
    elif state == 'end_set_min':
        clock.set_time(hour=hour_new, min=min_new)
    
    elif state == 'start_set_alarm_hour':
        hour = clock.get_alarm_hour()
        minute = clock.get_alarm_min()
        inputs.rezero()
    elif state == 'set_alarm_hour':
        hour_new = (hour + inputs.get_encoder_pos()) % 24
        segment_disp.print_2vals(halfblink(hour_new, blink_bool), minute)
    elif state == 'set_alarm_min':
        min_new = (minute + inputs.get_encoder_pos()) % 60
        segment_disp.print_2vals(hour_new, halfblink(min_new, blink_bool))
    elif state == 'end_set_min':
        clock.set_alarm(hour=hour_new, min=min_new)

    if date_str != clock.get_date_str():
        date_str = clock.get_date_str()
        inkdisp.modify_date(date_str)
        inkdisp.update()
    
    k += 1
    time.sleep(dt)
