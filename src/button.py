import digitalio


class Button:
    """
    Handles button presses
    """

    def __init__(self, pin):
        self.button_prev = False
        self.button = digitalio.DigitalInOut(pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP

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
