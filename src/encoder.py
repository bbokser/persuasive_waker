import rotaryio
import digitalio


class Encoder:
    """
    Handles encoder and button presses
    """

    def __init__(self, pinA, pinB):
        # encoder
        self.encoder = rotaryio.IncrementalEncoder(pinA, pinB)  # , divisor=2)
        self.zero_pos = self.encoder.position

    def rezero(self):
        # re-zero encoder
        self.zero_pos = self.encoder.position

    def get_encoder_pos(self):
        # encoder feedback
        return self.encoder.position - self.zero_pos
