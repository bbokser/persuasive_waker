import pwmio

class Piezo():
    def __init__(self, pin):
        self.buzzer = pwmio.PWMOut(pin, variable_frequency=False)
        # self.buzzer = pwmio.PWMOut(pin, variable_frequency=True)
        self.duty_max = 2**16  # max duty cycle = 65535 Hz
    
    def play(self, tone: int, amp: float, on: bool):
        '''
        note = note in tone dict, string
        amp = amplitude, between 0 and 1
        '''
        if on:
            # self.buzzer.frequency = int(tone)
            self.buzzer.duty_cycle = int(amp * self.duty_max)
        else:
            self.buzzer.duty_cycle = 0
    
    def shutoff(self):
        self.buzzer.duty_cycle = 0
        