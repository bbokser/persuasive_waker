import board
import pulseio
import adafruit_irremote

def fuzzy_pulse_compare(pulse1, pulse2, fuzzyness=0.2):
    # # SPDX-FileCopyrightText: 2019 Anne Barela for Adafruit Industries
    # https://learn.adafruit.com/ir-sensor/circuitpython
    if len(pulse1) != len(pulse2):
        return False
    for i in range(len(pulse1)):
        threshold = int(pulse1[i] * fuzzyness)
        if abs(pulse1[i] - pulse2[i]) > threshold:
            return False
    return True

class IrSensor():
    def __init__(self):
        self.pulses = pulseio.PulseIn(board.D4, maxlen=200, idle_state=True)
        self.decoder = adafruit_irremote.GenericDecode()
        self.pulse_expected = [9040, 4463, 573, 581, 571, 
                               583, 571, 582, 570, 584, 570, 
                               583, 571, 582, 571, 583, 571, 
                               583, 572, 1649, 570, 1652, 569, 
                               1650, 571, 1678, 543, 1653, 569, 
                               1650, 593, 1628, 570, 1649, 572, 
                               1653, 569, 582, 570, 1650, 572, 
                               583, 570, 583, 570, 583, 571, 
                               1653, 568, 583, 570, 583, 571, 
                               1649, 572, 583, 570, 1678, 544, 
                               1650, 571, 1653, 568, 582, 571, 
                               1650, 571]

    def check_ir(self, delay=0.1):
        pulses = self.pulses
        # note that this delays the loop 
        # while waiting to receive a signal
        pulse = self.decoder.read_pulses(pulses, blocking=False, blocking_delay=delay)
        if pulse is None:
            return False
        
        output = fuzzy_pulse_compare(self.pulse_expected, pulse)
        pulses.clear()
        return output