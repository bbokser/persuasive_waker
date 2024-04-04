
class State:
    def __init__(self, fsm):
        self.FSM = fsm

    def enter(self):
        pass

    def execute(self):
        pass

    def exit(self):
        pass


class Default(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        if self.FSM.set_date == True:
            self.FSM.to_transition('toSetYear')
            return str('start_set_year')
        elif self.FSM.set_time == True:
            self.FSM.to_transition('toSetHour')
            return str('start_set_hour')
        elif self.FSM.set_alarm1 == True:
            return str('start_set_alarm1')
        elif self.FSM.set_alarm2 == True:
            return str('start_set_alarm2')
        else:
            pass
        return str('default')

class SetYear(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        if self.FSM.enter == True:
            self.FSM.to_transition('toSetMonth')
            return str('start_set_month')
        elif self.FSM.back == True:
            self.FSM.to_transition('toDefault')
        else:
            pass
        return str('set_year')
    
class SetMonth(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        if self.FSM.enter == True:
            self.FSM.to_transition('toSetDay')
            return str('start_set_day')
        elif self.FSM.back == True:
            self.FSM.to_transition('toDefault')
        else:
            pass
        return str('set_month')
    
class SetDay(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        if self.FSM.enter == True:
            self.FSM.to_transition('toDefault')
            return str('end_set_day')
        elif self.FSM.back == True:
            self.FSM.to_transition('toDefault')
        else:
            pass
        return str('set_day')
    
class SetHour(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        if self.FSM.enter == True:
            self.FSM.to_transition('toSetMin')
            return str('start_set_min')
        elif self.FSM.back == True:
            self.FSM.to_transition('toDefault')
        else:
            pass
        return str('set_hour')
    
class SetMin(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def execute(self):
        if self.FSM.enter == True or self.FSM.back == True:
            self.FSM.to_transition('toDefault')
            return str('end_set_min')
        else:
            pass
        return str('set_min')


class Transition:
    def __init__(self, tostate):
        self.toState = tostate

    def execute(self):
        pass
        # return self.toState


class FSM:
    def __init__(self):
        self.states = {}
        self.transitions = {}
        self.curState = None
        self.prevState = None
        self.trans = None
        
        self.set_date = False
        self.set_time = False
        self.set_alarm1 = False
        self.set_alarm2 = False

        self.add_state('default', Default(self))
        self.add_state('set_year', SetYear(self))
        self.add_state('set_month', SetMonth(self))
        self.add_state('set_day', SetDay(self))
        self.add_state('set_hour', SetHour(self))
        self.add_state('set_min', SetMin(self))

        self.add_transition('toSetYear',      Transition('set_year'))
        self.add_transition('toSetMonth', Transition('set_month'))
        self.add_transition('toSetDay',    Transition('set_day'))
        self.add_transition('toSetHour',    Transition('set_hour'))
        self.add_transition('toSetMin',    Transition('set_min'))
        self.add_transition('toDefault',    Transition('default'))

        self.setstate('default')

    def add_transition(self, transname, transition):
        self.transitions[transname] = transition

    def add_state(self, statename, state):
        self.states[statename] = state

    def setstate(self, statename):
        # look for whatever state we passed in within the states dict
        self.prevState = self.curState
        self.curState = self.states[statename]

    def to_transition(self, to_trans):
        # set the transition state
        self.trans = self.transitions[to_trans]

    def execute(self, set_date, set_time, set_alarm1, set_alarm2):
        self.set_date = set_date
        self.set_time = set_time
        self.set_alarm1 = set_alarm1
        self.set_alarm2 = set_alarm2
        
        if self.trans:
            self.curState.exit()
            self.trans.execute()
            self.setstate(self.trans.toState)
            self.curState.enter()
            self.trans = None

        output = self.curState.execute()

        return output