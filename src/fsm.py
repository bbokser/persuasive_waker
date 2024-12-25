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
        rf_input = self.f.rf.update()
        if self.f.clock.get_alarm_status(rf_input) is True:
            self.f.to_transition("toAlarming")


class Alarming(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def execute(self):
        rf_input = self.f.rf.update()
        self.f.as1115.display_hourmin(self.f.clock.get_hour(), self.f.clock.get_min())
        alarm_delta = self.f.clock.get_alarm_delta()
        magnitude = utils.clip(
            abs(alarm_delta / self.f.clock.alarm_delta_max), 0.1, 1.0
        )
        tone = utils.translate(utils.clip(magnitude, 0.1, 1.0), 200, 400)
        self.f.buzzer.play(tone=tone, amp=magnitude, on=self.f.heartbeat)

        if self.f.clock.get_alarm_status(rf_input) == False:
            self.f.to_transition("toDefault")

    def exit(self):
        self.f.clock.reset_alarm()
        self.f.buzzer.shutoff()


class Default(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def execute(self):
        self.execute_default()
        self.f.seg_colon.on()
        self.f.as1115.display_hourmin(self.f.clock.get_hour(), self.f.clock.get_min())

        if self.f.b_set_date == True:
            self.f.to_transition("toSetYear")
        elif self.f.b_set_time == True:
            self.f.to_transition("toSetHour")
        elif self.f.b_set_alarm == True:
            self.f.to_transition("toSetAlarmHour")
        elif self.f.b_set_brightness == True:
            self.f.to_transition("toSetBrightness")
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
            self.f.to_transition("toDefault")
        elif self.f.b_back == True:
            self.f.to_transition("toDefault")
        else:
            pass

    def exit(self):
        self.f.clock.set_date(
            year=self.f.year_new, month=self.f.month_new, day=self.f.day_new
        )
        self.f.as1115.unwink()


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
            self.f.as1115.unwink()
            self.f.to_transition("toDefault")
        elif self.f.b_back == True:
            self.f.to_transition("toDefault")
        else:
            pass


class SetAlarmHour(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.hour = self.f.clock.get_alarm_hour()
        self.f.minute = self.f.clock.get_alarm_min()
        self.f.encoder.rezero()

    def execute(self):
        self.execute_default()
        self.f.hour_new = (self.f.hour + self.f.encoder.get_encoder_pos()) % 24
        self.f.as1115.display_hourmin(self.f.hour_new, self.f.minute)
        self.f.as1115.wink_left(self.f.heartbeat)

        if self.f.b_enter == True:
            self.f.to_transition("toSetAlarmMin")
        elif self.f.b_back == True:
            self.f.clock.disable_alarm()
            self.f.to_transition("toDefault")


class SetAlarmMin(State):
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
            self.f.clock.set_alarm(hour=self.f.hour_new, min=self.f.min_new)
            self.f.as1115.unwink()
            self.f.to_transition("toDefault")
        elif self.f.b_back == True:
            self.f.clock.disable_alarm()
            self.f.to_transition("toDefault")


class SetBrightness(State):
    def __init__(self, fsm, name):
        super().__init__(fsm, name)

    def enter(self):
        self.f.seg_colon.off()
        self.f.encoder.rezero()
        self.f.brightness_new = self.f.as1115.brightness

    def execute(self):
        self.execute_default()
        self.f.as1115.brightness = (
            self.f.brightness_new + self.f.encoder.get_encoder_pos()
        ) % 15 + 1  # minimum of 1 to prevent blinking from doing nothing
        self.f.as1115.display_int(self.f.as1115.brightness)
        self.f.seg_colon.set_brightness(self.f.as1115.brightness / 15)
        self.f.seg_apost.set_brightness(self.f.as1115.brightness / 15)

        if self.f.b_enter == True:
            self.f.to_transition("toDefault")
        elif self.f.b_back == True:
            self.f.to_transition("toDefault")


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
        self.add_state("set_alarm_hour", SetAlarmHour)
        self.add_state("set_alarm_min", SetAlarmMin)
        self.add_state("set_brightness", SetBrightness)

        self.add_transition("toAlarming", Transition("alarming"))
        self.add_transition("toSetYear", Transition("set_year"))
        self.add_transition("toSetMonth", Transition("set_month"))
        self.add_transition("toSetDay", Transition("set_day"))
        self.add_transition("toSetHour", Transition("set_hour"))
        self.add_transition("toSetMin", Transition("set_min"))
        self.add_transition("toSetAlarmHour", Transition("set_alarm_hour"))
        self.add_transition("toSetAlarmMin", Transition("set_alarm_min"))
        self.add_transition("toSetBrightness", Transition("set_brightness"))
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
