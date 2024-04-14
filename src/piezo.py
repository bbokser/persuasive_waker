import board
import pwmio

class Piezo():
    def __init__(self):
        self.buzzer = pwmio.PWMOut(board.D25, variable_frequency=True)
        self.duty_max = 2**16  # max duty cycle = 65535 Hz
        self.tone = {'c4': 262,
                     'd4': 294,
                     'e4': 330,
                     'f4': 359,
                     'g4': 392,
                     'a4': 440,
                     'b4': 494}
    
    def play(self, note: str, amp: float, on: bool):
        '''
        note = note in tone dict, string
        amp = amplitude, between 0 and 1
        '''
        if on:
            self.buzzer.frequency = self.tone[note]
            self.buzzer.duty_cycle = amp * self.duty_max
        else:
            self.buzzer.duty_cycle = 0
        