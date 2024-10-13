import board
import rotaryio
import digitalio

class Encoder():
    '''
    Handles encoder and button presses
    '''
    def __init__(self):
        # encoder
        self.encoder = rotaryio.IncrementalEncoder(board.GP8, board.GP9) #, divisor=2)
        self.zero_pos = self.encoder.position

        # encoder button (enter)
        self.button = self.config_button(board.GP10)
        self.button_prev = False

    def config_button(self, pin):
        button = digitalio.DigitalInOut(pin)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.UP
        return button
    
    def rezero(self):
        # re-zero encoder
        self.zero_pos = self.encoder.position

    def get_encoder_pos(self):
        # encoder feedback
        return self.encoder.position - self.zero_pos
        
    def update_button(self):
        # this must run every timestep to work
        if self.button_prev is True and self.get_button() is False:
            # button was previously pressed, is no longer pressed
            self.button_prev = False
            return True
        self.button_prev = self.get_button()
        return False
    
    def get_button(self):
        return not self.button.value
