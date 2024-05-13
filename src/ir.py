import board
import pulseio

class IrSensor():
    def __init__(self):
        self.pulses = pulseio.PulseIn(board.D4, maxlen=200, idle_state=True)

    def check_ir(self):
        pulses = self.pulses
        pulse_len = len(pulses)
        pulses.clear()
        pulses.resume()
        if pulse_len > 0:
            return True
        else:
            return False