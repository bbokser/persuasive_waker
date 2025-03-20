import pwmio
import utils
import time


class Piezo:
    def __init__(self, pin):
        # self.buzzer = pwmio.PWMOut(pin, variable_frequency=False)
        self.buzzer = pwmio.PWMOut(pin, variable_frequency=True)
        # self.duty_max = 2**16 - 1 # max duty cycle = 65535 Hz
        self.pitch = 200  # default pitch
        self.duty_min = 100
        self.duty_max = 2730

    def play(self, amp: float, pitch: int = None, on: bool = True):
        """
        pitch = frequency
        amp = amplitude, between 0 and 1
        on = way to turn on/off
        """
        if pitch is None:
            pitch = self.pitch

        if on:
            self.buzzer.frequency = int(pitch)
            self.buzzer.duty_cycle = int(
                utils.translate(amp, min=self.duty_min, max=self.duty_max)
            )
        else:
            self.buzzer.duty_cycle = 0

    def shutoff(self):
        self.buzzer.duty_cycle = 0

    def play_error_tone(self):
        self.buzzer.frequency = 100
        self.buzzer.duty_cycle = 1000
        time.sleep(0.1)

        self.buzzer.duty_cycle = 0
        time.sleep(0.1)

        self.buzzer.frequency = 100
        self.buzzer.duty_cycle = 1000
        time.sleep(0.1)

        self.buzzer.duty_cycle = 0
