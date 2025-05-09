import utils


class State:
    def __init__(self, fsm, name):
        self.f = fsm
        self.name = name

    def punch_in(self):
        print("enter ", self.name)

    def enter(self):
        pass

    def execute(self):
        pass

    def exit(self):
        pass

    def punch_out(self):
        print("exit ", self.name)

    def execute_default(self):
        if (
            self.f.clock.alarm1.get_status_init() is True
            or self.f.clock.alarm2.get_status_init() is True
        ):
            self.f.to_transition("toAlarming")


class Alarming(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.clock.alarm1.log_start()
        self.f.clock.alarm2.log_start()

    def execute(self):
        rf_input = self.f.rf.update()
        self.f.as1115.display_hourmin(self.f.clock.get_hour(), self.f.clock.get_min())
        self.f.buzzer.play(amp=1, on=self.f.heartbeat)

        if (
            self.f.clock.alarm1.get_status(rf_input) == False
            and self.f.clock.alarm2.get_status(rf_input) == False
        ):
            self.f.to_transition("toDefault")

    def exit(self):
        self.f.clock.alarm1.reset()
        self.f.clock.alarm2.reset()
        self.f.buzzer.shutoff()


class Default(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        # prevent from getting stuck in no-decode mode
        self.f.as1115.enable_decode()

    def execute(self):
        self.execute_default()
        self.f.seg_colon.on()
        self.f.as1115.display_hourmin(self.f.clock.get_hour(), self.f.clock.get_min())

        if self.f.b_set_date == True:
            if not self.f.rf._get_button():
                self.f.to_transition("toSetYear")
            else:
                self.f.buzzer.play_error_tone()
        elif self.f.b_set_time == True:
            if not self.f.rf._get_button():
                self.f.to_transition("toSetHour")
            else:
                self.f.buzzer.play_error_tone()
        elif self.f.b_set_alarm == True:
            if not self.f.rf._get_button():
                self.f.to_transition("toSetAlarm1Hour")
            else:
                self.f.buzzer.play_error_tone()
        elif self.f.b_set_brightness == True:
            self.f.to_transition("toSetBrightness")
        elif self.f.b_options == True:
            self.f.to_transition("toSetUnits")
        else:
            pass


class SetYear(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.seg_colon.off()
        self.f.year = self.f.clock.get_year()
        self.f.month = self.f.clock.get_month()
        self.f.day = self.f.clock.get_day()
        self.f.encoder.rezero()

    def execute(self):
        self.execute_default()
        self.f.year_new = utils.wrap_to_range(
            self.f.year + self.f.encoder.get_encoder_pos(), a=1970, b=2037
        )
        self.f.as1115.display_int(self.f.year_new)
        self.f.as1115.wink_left(self.f.heartbeat)
        self.f.as1115.wink_right(self.f.heartbeat)

        if self.f.b_enter == True:
            self.f.to_transition("toSetMonth")
        elif self.f.b_back == True:
            self.f.to_transition("toDefault")
        else:
            pass


class SetMonth(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()

    def execute(self):
        self.execute_default()
        self.f.month_new = utils.wrap_to_range(
            self.f.month + self.f.encoder.get_encoder_pos(), a=1, b=12
        )
        self.f.as1115.display_hourmin(self.f.month_new, self.f.day)
        self.f.as1115.wink_left(self.f.heartbeat)

        if self.f.b_enter == True:
            self.f.to_transition("toSetDay")
        elif self.f.b_back == True:
            self.f.to_transition("toDefault")
        else:
            pass


class SetDay(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()

    def execute(self):
        self.execute_default()
        day_max = utils.get_max_day(year=self.f.year_new, month=self.f.month_new)
        self.f.day_new = utils.wrap_to_range(
            self.f.day + self.f.encoder.get_encoder_pos(), a=1, b=day_max
        )
        self.f.as1115.display_hourmin(self.f.month_new, self.f.day_new)
        self.f.as1115.wink_right(self.f.heartbeat)

        if self.f.b_enter == True:
            self.f.clock.set_date(
                year=self.f.year_new, month=self.f.month_new, day=self.f.day_new
            )
            self.f.update_disp()
            self.f.to_transition("toDefault")
        elif self.f.b_back == True:
            self.f.to_transition("toDefault")
        else:
            pass


class SetHour(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.hour = self.f.clock.get_hour()
        self.f.minute = self.f.clock.get_min()
        self.f.encoder.rezero()

    def execute(self):
        self.execute_default()
        self.f.hour_new = (self.f.hour + self.f.encoder.get_encoder_pos()) % 24
        self.f.as1115.display_hourmin(self.f.hour_new, self.f.minute)
        self.f.as1115.wink_left(self.f.heartbeat)

        if self.f.b_enter == True:
            self.f.to_transition("toSetMin")
        elif self.f.b_back == True:
            self.f.to_transition("toDefault")
        else:
            pass


class SetMin(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()

    def execute(self):
        self.execute_default()
        self.f.min_new = (self.f.minute + self.f.encoder.get_encoder_pos()) % 60
        self.f.as1115.display_hourmin(self.f.hour_new, self.f.min_new)
        self.f.as1115.wink_right(self.f.heartbeat)

        if self.f.b_enter == True:
            self.f.clock.set_time(hour=self.f.hour_new, min=self.f.min_new)
            self.f.to_transition("toDefault")
        elif self.f.b_back == True:
            self.f.to_transition("toDefault")
        else:
            pass


class SetAlarm1Hour(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.hour = self.f.clock.alarm1.get_hour()
        self.f.minute = self.f.clock.alarm1.get_min()
        self.f.wdays = self.f.clock.alarm1.wday_set
        self.f.encoder.rezero()

    def execute(self):
        self.execute_default()
        self.f.hour_new = (self.f.hour + self.f.encoder.get_encoder_pos()) % 24
        self.f.as1115.display_hourmin(self.f.hour_new, self.f.minute)
        self.f.as1115.wink_left(self.f.heartbeat)

        if self.f.b_enter == True:
            self.f.to_transition("toSetAlarm1Min")
        elif self.f.b_back == True:
            self.f.clock.alarm1.disable()
            self.f.update_disp()
            self.f.to_transition("toDefault")
        elif self.f.b_set_alarm == True:
            self.f.to_transition("toSetAlarm2Hour")


class SetAlarm1Min(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()

    def execute(self):
        self.execute_default()
        self.f.min_new = (self.f.minute + self.f.encoder.get_encoder_pos()) % 60
        self.f.as1115.display_hourmin(self.f.hour_new, self.f.min_new)
        self.f.as1115.wink_right(self.f.heartbeat)

        if self.f.b_enter == True:
            self.f.to_transition("toSetAlarm1Wdays")
            # self.f.clock.alarm1.set_alarm(hour=self.f.hour_new, min=self.f.min_new)
            # self.f.to_transition("toDefault")
        elif self.f.b_back == True:
            self.f.clock.alarm1.disable()
            self.f.update_disp()
            self.f.to_transition("toDefault")


class SetAlarm1Wdays(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.seg_colon.off()
        self.f.encoder.rezero()

    def execute(self):
        self.execute_default()
        self.f.wdays_new = (self.f.wdays + self.f.encoder.get_encoder_pos()) % 3
        if self.f.wdays_new == 0:
            self.f.as1115.display_fullweek()
        elif self.f.wdays_new == 1:
            self.f.as1115.display_workdays()
        elif self.f.wdays_new == 2:
            self.f.as1115.display_weekend()

        self.f.as1115.wink_left(self.f.heartbeat)
        self.f.as1115.wink_right(self.f.heartbeat)

        if self.f.b_enter == True:
            self.f.clock.alarm1.set_alarm(
                hour=self.f.hour_new, min=self.f.min_new, wday_set=self.f.wdays_new
            )
            self.f.to_transition("toDefault")
        elif self.f.b_back == True:
            self.f.clock.alarm1.disable()
            self.f.to_transition("toDefault")

    def exit(self):
        self.f.update_disp()


class SetAlarm2Hour(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.hour = self.f.clock.alarm2.get_hour()
        self.f.minute = self.f.clock.alarm2.get_min()
        self.f.wdays = self.f.clock.alarm2.wday_set
        self.f.encoder.rezero()

    def execute(self):
        self.execute_default()
        self.f.hour_new = (self.f.hour + self.f.encoder.get_encoder_pos()) % 24
        self.f.as1115.display_hourmin(self.f.hour_new, self.f.minute)
        self.f.as1115.wink_left(self.f.heartbeat)

        if self.f.b_enter == True:
            self.f.to_transition("toSetAlarm2Min")
        elif self.f.b_back == True:
            self.f.clock.alarm2.disable()
            self.f.update_disp()
            self.f.to_transition("toDefault")


class SetAlarm2Min(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.encoder.rezero()

    def execute(self):
        self.execute_default()
        self.f.min_new = (self.f.minute + self.f.encoder.get_encoder_pos()) % 60
        self.f.as1115.display_hourmin(self.f.hour_new, self.f.min_new)
        self.f.as1115.wink_right(self.f.heartbeat)

        if self.f.b_enter == True:
            self.f.to_transition("toSetAlarm2Wdays")
            # self.f.clock.alarm2.set_alarm(hour=self.f.hour_new, min=self.f.min_new)
            # self.f.to_transition("toDefault")
        elif self.f.b_back == True:
            self.f.clock.alarm2.disable()
            self.f.update_disp()
            self.f.to_transition("toDefault")


class SetAlarm2Wdays(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.seg_colon.off()
        self.f.encoder.rezero()

    def execute(self):
        self.execute_default()
        self.f.wdays_new = (self.f.wdays + self.f.encoder.get_encoder_pos()) % 3
        if self.f.wdays_new == 0:
            self.f.as1115.display_fullweek()
        elif self.f.wdays_new == 1:
            self.f.as1115.display_workdays()
        elif self.f.wdays_new == 2:
            self.f.as1115.display_weekend()

        self.f.as1115.wink_left(self.f.heartbeat)
        self.f.as1115.wink_right(self.f.heartbeat)

        if self.f.b_enter == True:
            self.f.clock.alarm2.set_alarm(
                hour=self.f.hour_new, min=self.f.min_new, wday_set=self.f.wdays_new
            )
            self.f.to_transition("toDefault")
        elif self.f.b_back == True:
            self.f.clock.alarm2.disable()
            self.f.to_transition("toDefault")

    def exit(self):
        self.f.update_disp()


class SetBrightness(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.seg_colon.off()
        self.f.encoder.rezero()
        self.f.brightness_original = self.f.as1115.brightness

    def execute(self):
        self.execute_default()
        # minimum of 1 to prevent blinking from doing nothing
        self.f.as1115.brightness = utils.wrap_to_range(
            self.f.brightness_original + self.f.encoder.get_encoder_pos(), 1, 15
        )
        self.f.as1115.display_int(self.f.as1115.brightness)
        self.f.seg_colon.set_brightness(self.f.as1115.brightness / 15)
        self.f.seg_apost.set_brightness(self.f.as1115.brightness / 15)

        if self.f.b_enter == True:
            self.f.to_transition("toDefault")
        elif self.f.b_back == True:
            self.f.as1115.brightness = self.f.brightness_original
            self.f.to_transition("toDefault")


class SetUnits(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.seg_colon.off()
        self.f.encoder.rezero()
        self.f.units_new = self.f.sensor.units

    def execute(self):
        self.execute_default()
        self.f.units_new = (self.f.sensor.units + self.f.encoder.get_encoder_pos()) % 2
        if self.f.units_new == 0:
            self.f.as1115.display_letter("C")
        else:
            self.f.as1115.display_letter("F")
        self.f.as1115.wink_right(self.f.heartbeat)
        if self.f.b_enter == True:
            self.f.sensor.change_units(self.f.units_new)
            self.f.update_disp()
            self.f.to_transition("toDefault")
        elif self.f.b_back == True:
            self.f.to_transition("toDefault")
        elif self.f.b_options == True:
            self.f.to_transition("toSetPitch")


class SetPitch(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.as1115.enable_decode()
        self.f.seg_colon.off()
        self.f.encoder.rezero()
        self.f.pitch_new = self.f.buzzer.pitch

    def execute(self):
        self.execute_default()
        # https://www.mouser.com/datasheet/2/1628/css_i4b20_smt_tr-3509940.pdf
        self.f.pitch_new = int(
            utils.wrap_to_range(
                int(self.f.buzzer.pitch / 50) + self.f.encoder.get_encoder_pos(), 1, 10
            )
            * 50
        )
        self.f.as1115.display_int(self.f.pitch_new)
        self.f.buzzer.play(amp=0.25, pitch=self.f.pitch_new)

        if self.f.b_enter == True:
            self.f.buzzer.pitch = self.f.pitch_new
            self.f.to_transition("toDefault")
        elif self.f.b_back == True:
            self.f.to_transition("toDefault")

    def exit(self):
        self.f.buzzer.shutoff()


class Transition:
    def __init__(self, tostate):
        self.toState = tostate

    def execute(self):
        # return self.toState
        pass


class FSM:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

        self.states = {}
        self.transitions = {}
        self.curState = None
        self.prevState = None
        self.trans = None

        self.add_state("default", Default)
        self.add_state("alarming", Alarming)
        self.add_state("set_year", SetYear)
        self.add_state("set_month", SetMonth)
        self.add_state("set_day", SetDay)
        self.add_state("set_hour", SetHour)
        self.add_state("set_min", SetMin)
        self.add_state("set_alarm1_hour", SetAlarm1Hour)
        self.add_state("set_alarm1_min", SetAlarm1Min)
        self.add_state("set_alarm1_wdays", SetAlarm1Wdays)
        self.add_state("set_alarm2_hour", SetAlarm2Hour)
        self.add_state("set_alarm2_min", SetAlarm2Min)
        self.add_state("set_alarm2_wdays", SetAlarm2Wdays)
        self.add_state("set_brightness", SetBrightness)
        self.add_state("set_units", SetUnits)
        self.add_state("set_pitch", SetPitch)

        self.add_transition("toAlarming", Transition("alarming"))
        self.add_transition("toSetYear", Transition("set_year"))
        self.add_transition("toSetMonth", Transition("set_month"))
        self.add_transition("toSetDay", Transition("set_day"))
        self.add_transition("toSetHour", Transition("set_hour"))
        self.add_transition("toSetMin", Transition("set_min"))
        self.add_transition("toSetAlarm1Hour", Transition("set_alarm1_hour"))
        self.add_transition("toSetAlarm1Min", Transition("set_alarm1_min"))
        self.add_transition("toSetAlarm1Wdays", Transition("set_alarm1_wdays"))
        self.add_transition("toSetAlarm2Hour", Transition("set_alarm2_hour"))
        self.add_transition("toSetAlarm2Min", Transition("set_alarm2_min"))
        self.add_transition("toSetAlarm2Wdays", Transition("set_alarm2_wdays"))
        self.add_transition("toSetBrightness", Transition("set_brightness"))
        self.add_transition("toSetUnits", Transition("set_units"))
        self.add_transition("toSetPitch", Transition("set_pitch"))
        self.add_transition("toDefault", Transition("default"))

        self.setstate("default")

    def add_transition(self, transname, transition):
        self.transitions[transname] = transition

    def add_state(self, statename, state):
        self.states[statename] = state(self, statename)

    def setstate(self, statename):
        # look for whatever state we passed in within the states dict
        self.prevState = self.curState
        self.curState = self.states[statename]

    def to_transition(self, to_trans):
        # set the transition state
        self.trans = self.transitions[to_trans]

    def execute(self):
        if self.trans:
            # prevents seg disp from getting stuck in a wink/blink
            self.as1115.unwink()

            self.curState.exit()
            if self.verbose is True:
                self.curState.punch_out()
            self.trans.execute()
            self.setstate(self.trans.toState)
            if self.verbose is True:
                self.curState.punch_in()
            self.curState.enter()
            self.trans = None

        self.curState.execute()
