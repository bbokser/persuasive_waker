import board
import rotaryio
import digitalio

class Inputs():
    '''
    Handles encoder and button presses
    '''
    def __init__(self):
        # encoder
        self.encoder = rotaryio.IncrementalEncoder(board.D10, board.D9) #, divisor=2)
        self.zero_pos = self.encoder.position

        # encoder button
        button = digitalio.DigitalInOut(board.D11)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.UP
        self.button = button
        self.button_val_prev = False

        # set date button
        button_d = digitalio.DigitalInOut(board.D12)
        button_d.direction = digitalio.Direction.INPUT
        button_d.pull = digitalio.Pull.UP
        self.button_d = button_d

        # set time button
        button_t = digitalio.DigitalInOut(board.D13)
        button_t.direction = digitalio.Direction.INPUT
        button_t.pull = digitalio.Pull.UP
        self.button_t = button_t

        # set alarm button
        button_a = digitalio.DigitalInOut(board.D5)
        button_a.direction = digitalio.Direction.INPUT
        button_a.pull = digitalio.Pull.UP
        self.button_a = button_a

        # set blinds button
        button_b = digitalio.DigitalInOut(board.D6)
        button_b.direction = digitalio.Direction.INPUT
        button_b.pull = digitalio.Pull.UP
        self.button_b = button_b
    
    def update_button(self):
        # this must run every timestep to work
        if self.button_val_prev is True and self.button.value is False:
            # button was previously pressed, is no longer pressed
            self.button_val_prev = False
            return True
        
        self.button_val_prev = self.button.value
        return False
        
    def rezero(self):
        # re-zero encoder
        self.zero_pos = self.encoder.position

    def get_encoder_pos(self):
        # encoder feedback
        return self.encoder.position - self.zero_pos
        
