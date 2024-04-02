import time

from inkdisp import InkDisp
from clock import Clock
from segment import SegmentDisp
from fsm import FSM

time.sleep(5)  # to ensure serial connection does not fail

fsm = FSM()
segment_disp = SegmentDisp()
clock = Clock()

date_str = clock.get_date_str()
inkdisp = InkDisp(date_str)
# inkdisp.add_text(date_str, x=inkdisp.width//2, y=inkdisp.height//2, color='black')

while True:
    state = fsm.execute(setting=0)
    print(state)
    if state == 'default':
        segment_disp.print_2vals(clock.get_hour(), clock.get_min())
    elif state == 'set_year':
        year = clock.get_year()
        segment_disp.print(year)
        clock.increase_year()
    elif state == 'set_month':
        segment_disp.print_2vals(clock.get_month(), clock.get_day())
        clock.increase_month()
    elif state == 'set_day':
        segment_disp.print_2vals(clock.get_month(), clock.get_day())
        clock.increase_day()
    elif state == 'set_hour':
        segment_disp.print_2vals(clock.get_hour(), clock.get_min())
        clock.increase_hour()
    elif state == 'set_min':
        segment_disp.print_2vals(clock.get_hour(), clock.get_min())
        clock.increase_min()

    if date_str != clock.get_date_str():
        date_str = clock.get_date_str()
        inkdisp.modify_date(date_str)
        inkdisp.update()
    time.sleep(0.1)
